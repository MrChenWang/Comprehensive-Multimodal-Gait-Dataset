import os
import os.path as osp
import csv
import cv2
import random


def video2frames(root_path, save_format="jpg",interval=1):
    def cut_frames(video_path, save_path):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Video info: Video path: {save_path}, Total frames: {total_frames}, FPS: {fps:.2f}")
        current_frame = 0
        while True:
            ret, frame = cap.read()
            if not(ret):
                break
            if current_frame % interval == 0:
                cv2.imwrite(osp.join(save_path, str(current_frame * 20)) + "." + save_format, frame)
            current_frame += 1
        cap.release()

    for file in os.listdir(root_path):
        for sub_file in os.listdir(osp.join(root_path, file)):
            video_paths = []
            video_names = []
            for f in os.listdir(osp.join(root_path, file, sub_file)):
                if f.endswith(".mp4"):
                    video_paths.append(osp.join(root_path, file, sub_file, f))
                    video_names.append(f.split(".")[0])
            for i in range(len(video_names)):
                save_path = osp.join(root_path, file, sub_file, video_names[i])
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                cut_frames(video_paths[i], save_path)



def generator_train_val(root_path, ratio=0.2):
    total_path = []
    for file in os.listdir(root_path):
        for sp in os.listdir(osp.join(root_path, file)):
            sub_path = os.path.join(root_path, file, sp)
            if os.path.exists(sub_path):
                total_path.append(sub_path)
            else:
                print("Could not find file!")

    val_path = random.sample(total_path, int(len(total_path)*ratio))
    train_path = [item for item in total_path if item not in val_path]
    print("Train counts/Validation counts:", len(train_path), len(val_path))
    # save txt
    with open(osp.join(root_path, "train.txt"), "w", encoding="utf-8") as f:
        for item in train_path:
            f.write(item + "\n")
    with open(osp.join(root_path, "val.txt"), "w", encoding="utf-8") as f:
        for item in val_path:
            f.write(item + "\n")
    with open(osp.join(root_path, "total.txt"), "w", encoding="utf-8") as f:
        for item in total_path:
            f.write(item + "\n")

def find_max_min_value(root_path):
    def read_csv(csv_path):
        data = []
        with open(csv_path, 'r', newline='') as f:
            csv_reader = csv.reader(f)
            header = next(csv_reader)
            #print("CSV header: ", header)
            for row in csv_reader:
                data.append(row[1:])
        return data

    max_angles = [0.0] * 7
    min_angles = [0.0] * 7
    max_gyro = [0.0] * 7
    min_gyro = [0.0] * 7
    max_pressure = [0] * 96
    min_pressure = [0] * 96

    for file in os.listdir(root_path):
        for sp in os.listdir(osp.join(root_path, file)):
            sub_path = os.path.join(root_path, file, sp)
            angle_file = osp.join(sub_path, 'IMU_angle.csv')
            gyro_file = osp.join(sub_path, 'IMU_gyro.csv')
            fp_file = osp.join(sub_path, 'Foot_pressure.csv')
            angle_data = read_csv(angle_file)
            for item in angle_data:
                max_angles = [max(max_angles[i], float(item[i])) for i in range(7)]
                min_angles = [min(min_angles[i], float(item[i])) for i in range(7)]
            gyro_data = read_csv(gyro_file)
            for item in gyro_data:
                max_gyro = [max(max_gyro[i], float(item[i])) for i in range(7)]
                min_gyro = [min(min_gyro[i], float(item[i])) for i in range(7)]
            fp_data = read_csv(fp_file)
            for item in fp_data:
                max_pressure = [max(max_pressure[i], int(item[i])) for i in range(96)]
                min_pressure = [min(min_pressure[i], int(item[i])) for i in range(96)]

    print("List of max angles: ", max_angles)
    print("List of min angles: ", min_angles)
    print("List of max gyros: ", max_gyro)
    print("List of min gyros: ", min_gyro)
    print("List of max foot pressure: ", max_pressure)
    print("List of min foot pressure: ", min_pressure)


if __name__ == "__main__":
    #video2frames("G:\\ExoDataCollect\\Data_public")
    #generator_train_val("G:\\ExoDataCollect\\Data_public")
    find_max_min_value("G:\\ExoDataCollect\\Data_public")