########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\services\api_server_service\executors.py total lines 182 
########################################################################

import asyncio
import threading
import json
import uuid
import time

class ExecutorMixin:
    def update_job_status(self, job_id: str, status_data: dict):
        with self.job_statuses_lock:
            if job_id not in self.job_statuses:
                self.job_statuses[job_id] = {}
            if "user_context" in status_data:
                self.job_statuses[job_id]["user_context"] = status_data.pop("user_context")
            self.job_statuses[job_id].update(status_data)
            if self.event_bus:
                active_jobs = []
                for j_id, j_data in self.job_statuses.items():
                    if j_data.get("status") == "RUNNING":
                        start_time = j_data.get("start_time", 0)
                        duration = time.time() - start_time
                        active_jobs.append(
                            {
                                "id": j_id,
                                "preset": j_data.get("preset_name", "N/A"),
                                "duration_seconds": round(duration, 2),
                                "user_context": j_data.get("user_context")
                            }
                        )
                self.event_bus.publish(
                    "DASHBOARD_ACTIVE_JOBS_UPDATE",
                    {"active_jobs": active_jobs},
                    publisher_id=self.service_id,
                )

    def get_job_status(self, job_id: str) -> dict | None:
        with self.job_statuses_lock:
            return self.job_statuses.get(job_id)

    async def trigger_workflow_by_api(
        self,
        preset_name: str,
        initial_payload: dict = None,
        raw_workflow_data: dict = None,
        start_node_id: str = None,
        mode: str = "EXECUTE",
        user_context: dict = None,
    ) -> str | None:

        workflow_data = None
        trigger_source_log = ""

        is_module_run = False
        if preset_name and ("_module" in preset_name or "_v" in preset_name or "researcher" in preset_name or "downloader" in preset_name):
             is_module_run = True

        self.kernel.write_to_log(f"[Trigger] DEBUG: Preset='{preset_name}', IsModule={is_module_run}", "DEBUG")

        if is_module_run:
             self.kernel.write_to_log(f"[Trigger] Detected Module Run request for: {preset_name}", "INFO")
        elif raw_workflow_data:
            self.kernel.write_to_log("Triggering workflow from raw data provided by API call.", "DEBUG")
            workflow_data = raw_workflow_data
            trigger_source_log = "raw API call"
        elif self.preset_manager:
            self.kernel.write_to_log(f"Triggering workflow from saved preset: '{preset_name}'", "DEBUG")
            user_id = user_context.get("user_id") if user_context else None
            workflow_data = self.preset_manager.get_preset_data(preset_name, user_id=user_id)
            trigger_source_log = f"preset '{preset_name}'"
        else:
            self.kernel.write_to_log(
                f"API Trigger failed: PresetManager service is not available.", "ERROR"
            )
            return None

        if not workflow_data and not is_module_run:
            self.kernel.write_to_log(
                f"API Trigger failed: workflow data for {trigger_source_log} not found or is empty.",
                "ERROR",
            )
            return None

        if initial_payload is None: initial_payload = {}
        if not isinstance(initial_payload, dict):
            initial_payload = {"data": {"value_from_trigger": initial_payload}}
        if "data" not in initial_payload: initial_payload["data"] = {}
        if "history" not in initial_payload: initial_payload["history"] = []
        initial_payload["data"]["user_context"] = user_context

        job_id = str(uuid.uuid4())
        initial_status = {
            "type": "workflow" if not is_module_run else "module_run",
            "status": "QUEUED",
            "preset_name": preset_name if not raw_workflow_data else "Raw Execution",
            "start_time": time.time(),
            "user_context": user_context
        }
        self.update_job_status(job_id, initial_status)

        self.kernel.write_to_log(
            f"Job '{job_id}' for {trigger_source_log or preset_name} has been queued. User Context: {user_context}", "INFO"
        )

        workflow_executor = self.kernel.get_service("workflow_executor_service")
        if workflow_executor:
            if hasattr(workflow_executor, 'execute_workflow_legacy_sync_runner'):
                nodes_list = workflow_data.get("nodes", [])
                connections_list = workflow_data.get("connections", [])
                nodes_dict = {node["id"]: node for node in nodes_list}
                connections_dict = {conn["id"]: conn for conn in connections_list}
                global_loop_config = workflow_data.get("global_loop_config")

                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    workflow_executor.execute_workflow_legacy_sync_runner,
                    nodes_dict,
                    connections_dict,
                    initial_payload,
                    self.kernel.write_to_log,
                    lambda *args: None,
                    lambda *args: None,
                    job_id,
                    self.update_job_status,
                    start_node_id,
                    mode,
                    user_context,
                    global_loop_config,
                    preset_name if not raw_workflow_data else "Raw Execution"
                )

            elif hasattr(workflow_executor, 'execute_standalone_node'):

                self.kernel.write_to_log(f"[Trigger] Legacy Runner missing. Forcing execute_standalone_node for '{preset_name}'...", "WARN")
                standalone_payload = {
                    "node_id": preset_name, # Here preset_name acts as module_id
                    "user_id": user_context.get("user_id") if user_context else "system",
                    "input": initial_payload,
                    "execution_id": job_id, # [Critical] Pass job_id so status updates match
                    "job_id": job_id # Redundant but safe
                }
                await workflow_executor.execute_standalone_node(standalone_payload)

            else:
                self.kernel.write_to_log(
                    f"CRITICAL: WorkflowExecutor does not support legacy runner AND missing execute_standalone_node. Cannot execute.",
                    "ERROR"
                )
                fail_status = {
                    "status": "FAILED",
                    "error": "Executor mismatch (DB vs Legacy).",
                    "end_time": time.time(),
                    "user_context": user_context
                }
                self.update_job_status(job_id, fail_status)
                return None

        else:
            self.kernel.write_to_log(
                f"Cannot trigger workflow {trigger_source_log}, WorkflowExecutor service is unavailable (likely due to license tier).",
                "ERROR",
            )
            fail_status = {
                "status": "FAILED",
                "error": "WorkflowExecutor service unavailable.",
                "end_time": time.time(),
                "user_context": user_context
            }
            self.update_job_status(job_id, fail_status)
            return None
        return job_id

    def trigger_scan_by_api(self, scanner_id: str = None) -> str | None:


        self.kernel.write_to_log("API Scan Trigger ignored: Diagnostics Service removed.", "WARN")
        return None
