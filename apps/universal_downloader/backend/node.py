########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\apps\universal_downloader\backend\node.py total lines 50 
########################################################################

import logging
import traceback
from flowork_kernel.flow_sdk.base_app_node import BaseAppNode
from .service import UniversalDownloaderService as DownloaderService

class DownloaderNode(BaseAppNode):
    def __init__(self, node_id, properties, kernel):
        super().__init__(node_id, properties, kernel)
        self.logger = logging.getLogger(f"App.Downloader.{node_id}")
        self.downloader_service = DownloaderService(kernel, "internal_dl_node")
        self.logger.info(f"DownloaderNode {node_id} ready.")

    async def execute(self, input_data):
        self.update_status("🔍 Resolving target URL...", "RUNNING")

        user_id = self.context.get("user_context", {}).get("user_id", "anonymous")

        target_url = self.resolve_variable(self.properties.get("url", ""))
        format_mode = self.properties.get("format_mode", "best")
        custom_output = self.properties.get("output_dir")

        if not target_url:
            return self.error("No URL provided to neural fetcher.", output_name="error")

        try:
            self.update_status(f"⚡ Ingesting: {target_url}", "RUNNING")


            job_id = self.downloader_service.start_download_task(target_url, user_id, {"output_folder": custom_output, "format": format_mode})
            self.downloader_service.execute_download(job_id, target_url, user_id, {"output_folder": custom_output, "format": format_mode})

            job_status = self.downloader_service.get_job_progress(job_id)

            if job_status.get("status") == "completed":
                self.logger.info(f"Fetch success")
                return self.success({"status": "downloaded", "url": target_url}, output_name="success")
            else:
                return self.error(job_status.get("error", "Unknown engine failure"), output_name="error")

        except Exception as e:
            err_msg = f"Kernel Panic in Downloader: {str(e)}"
            self.logger.error(err_msg)
            self.logger.error(traceback.format_exc())
            return self.error(err_msg, output_name="error")
