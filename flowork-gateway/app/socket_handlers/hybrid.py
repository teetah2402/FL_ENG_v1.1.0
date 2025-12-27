from flask import request, current_app

def register_handlers(sio):
    # =========================================================================
    # [HYBRID BRIDGE HANDLERS]
    # Menjembatani Komunikasi Python Node (Core) <-> Browser (Frontend)
    # =========================================================================

    @sio.on('app_action_response', namespace='/gui-socket')
    def on_gui_app_action_response(data):
        """
        Handler saat Browser selesai menjalankan tugas (misal: scraping) dan lapor balik.
        Flow: Browser -> Gateway (GUI Socket) -> Core (Engine Socket)
        """
        app = current_app._get_current_object()
        request_id = data.get('request_id')

        app.logger.info(f"[Hybrid Bridge] Fwd Response {request_id} from GUI -> Engines")

        # Broadcast ke semua engine (karena kita gak tau job ini milik engine mana secara spesifik di payload ini)
        # Di production, idealnya payload bawa 'engine_id' biar unicast.
        sio.emit('app_action_response', data, namespace='/engine-socket')

    @sio.on('app_action_request', namespace='/engine-socket')
    def on_engine_app_action_request(data):
        """
        Handler saat Core (Python) meminta tolong ke Browser.
        Flow: Core -> Gateway (Engine Socket) -> Browser (GUI Socket)
        """
        app = current_app._get_current_object()
        target_session = data.get('target_session', 'broadcast')
        action = data.get('action')

        app.logger.info(f"[Hybrid Bridge] Fwd Request '{action}' from Core -> GUI Room: {target_session}")

        if target_session == 'broadcast':
            # Kirim ke semua browser yang konek (Testing Mode)
            sio.emit('app_action_request', data, namespace='/gui-socket')
        else:
            # Kirim ke browser spesifik (Production Mode)
            sio.emit('app_action_request', data, room=target_session, namespace='/gui-socket')