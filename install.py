import launch

if not launch.is_installed("cv2.ximgproc"):
    launch.run_pip(
        "install opencv-contrib-python",
        "requirements for Adverse Cleaner",
    )
