import launch

if not launch.is_installed("opencv-contrib-python"):
    launch.run_pip(
        "install opencv-contrib-python",
        "requirements for Adverse Cleaner",
    )

# if not launch.is_installed("opencv-contrib-python"):
#     launch.run_pip(
#         "install opencv-contrib-python --user",
#         "requirements for Adverse Cleaner",
#     )