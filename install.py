import launch

if not launch.is_installed("cv2.ximgproc"):
    launch.run_pip(
        "install opencv-contrib-python --user",
        "requirements for Adverse Cleaner",
    )