# A Comprehensive Multimodal Gait Dataset for Indoor and Outdoor Locomotion

We built a multimodal gait dataset from 17 healthy participants (7 females and 10 males; age: 19–34 years; 
height: 173.2±8.88 cm; weight: 67.0±11.97 kg) across diverse indoor and outdoor environments. 
The dataset contains motion data from 7 IMUs, foot pressure data from FSR with 96 points, and visual data from 3 front-facing
cameras. The annotations include 16 classes of lower-limb locomotion states, gait phases for both legs,
and COP for both feet.

Here we provide several tools for quick access to the dataset.

## Demo of visualization tool
<img src=".\materials\GUI.gif" width="640" height="360"/>

As shown in the GUI, the 3 upper controls display the forward visual information during walking.
The cameras on both sides are installed on the thighs, and the middle camera is installed on the waist. 

The 3 lower controls, from left to right, respectively present the plantar pressure heat map and center of pressure position, 
the motion states in the sagittal plane, as well as the angles and angular velocities measured by the IMUs. 

The bottom panel integrates several basic functions, including selecting data folders and some basic interface controls.

## Getting Started
To get started, create a new Python virtual environment and install the required dependencies.
Our project is not tied to specific package versions. The environment and dependencies we used are listed below.

```//conda
conda create -n normal python=3.9
conda activate normal
```
```//conda
pip install pyqt5==5.15.11
pip install pyqtgraph==0.13.7
pip install tqdm==4.67.3
pip install opencv-python==4.13.0.92
pip install numpy==2.0.2
```
## Downloading Dataset
Please download the full dataset via the link:
[https://doi.org/10.6084/m9.figshare.32513229](https://doi.org/10.6084/m9.figshare.32513229)

## Usage Note
Once the dataset is downloaded, make a new folder as the **root path** and unzip all compressed files into the **root path**. And then follow the instructions below:

1.Execute **video2frames** from **utils.py** to turn original MP4 videos into a series of JPG frames.

2.Modify the **root path** on line 21 of **visualization_tool.py**, after that, you can run **visualization_tool.py**.

3.Execute **generator_train_val** from **utils.py** to split the dataset into training set and validation set.

4.Execute **find_max_min_value** from **utils.py** to get max and min values for data normalization.

## File Structure
There are 8 files in each subfolder. Their details are shown in the following table:

| File name              | Contents                                                                           | Unit              |
|------------------------|------------------------------------------------------------------------------------|-------------------|
| Annotations.csv        | The 16 terrain classes of current locomotion and the phases of left and right legs | None              |
| Center_of_pressure.csv | Normalized unilateral COP coordinates (left & right foot)                          | None              |
| Foot_pressure.csv      | Pressure values at each foot point (left & right)                                  | gram-force        |
| IMU_angle.csv          | Sagittal plane angles of lower limb joints                                         | degree            |
| IMU_gyro.csv           | Sagittal plane angular velocities of lower limb joints                             | degree per second |
| L_leg.mp4              | Left leg camera video                                                              | None              |
| M_hip.mp4              | Waist camera video                                                                 | None              |
| R_leg.mp4              | Right leg camera video                                                             | None              |

## License
This project is licensed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) 

## Future Work

We will expand the number of participants and add semantic segmentation labels for environmental images.

## Contact
If you have any questions or suggestions, feel free to contact us at this email: wangc@zstu.edu.cn

