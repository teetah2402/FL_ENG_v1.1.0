import os

def run(service, app_id, cell_name, code, *args, **kwargs):
    """
    Menulis Atomic Cell (.py) ke folder logic aplikasi tertentu.
    Mematuhi prinsip 1 File = 1 Fungsi.
    """
    try:
        # Ambil path aplikasi dari AppService
        app_service = service.kernel.get_service('app_service')
        if not app_service:
            return {"status": "error", "message": "AppService not found"}

        app_dir = os.path.join(app_service.base_app_path, app_id)
        logic_dir = os.path.join(app_dir, "logic")

        # Pastikan folder logic ada
        if not os.path.exists(logic_dir):
            os.makedirs(logic_dir)

        # Path file .py yang akan dibuat
        file_path = os.path.join(logic_dir, f"{cell_name}.py")

        # Template standar Atomic Cell Flowork
        # Kita bungkus code user ke dalam fungsi run() jika belum ada
        final_code = code
        if "def run" not in code:
            # FIX: Pindahkan logika replace ke luar f-string untuk menghindari SyntaxError backslash
            # Kode lama yang menyebabkan error:
            # final_code = f"def run(app_context, *args, **kwargs):\n    {code.replace('\\n', '\\n    ')}"

            # Perbaikan: Lakukan indentasi secara terpisah
            indented_body = code.replace('\n', '\n    ')
            final_code = f"def run(app_context, *args, **kwargs):\n    {indented_body}"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(final_code)

        return {
            "status": "success",
            "message": f"Atomic Cell '{cell_name}' created in '{app_id}'",
            "path": file_path
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}