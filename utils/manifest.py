import os
import pandas as pd
from utils.path import get_resource_path


class HscodeError(Exception):
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


def read_excel_file(file_path, dtype):
    current_directory = os.getcwd()
    print("Current working directory:", current_directory)
    # print(os.listdir(current_directory))
    return pd.read_excel(file_path, dtype=dtype)


def write_output_file(file_path, manifest_outputs):
    with open(file_path, 'w') as file:
        for manifest in manifest_outputs:
            file.write(manifest + "\n")


def write_output_excel(manifest_data_frames, indices, output_directory, prefix="manifest"):
    os.makedirs(output_directory, exist_ok=True)
    for df, (start_idx, end_idx) in zip(manifest_data_frames, indices):
        output_path = os.path.join(output_directory, f'{prefix}_{start_idx}_{end_idx}.xlsx')
        df.to_excel(output_path, index=False)


# 使用check_hscode函数检查输入文件中是否包含负值HSCode。负值HSCode列表是从配置文件hs_negative.csv中加载的。
# 若存在负值HSCode，程序会显示这些项目，并终止处理。
def check_hscode(input_file):
    if 'HSCode' not in input_file.columns:
        raise HscodeError("Input file must contain 'HSCode' column.")
    # 检查非法 hscode
    csv_path = get_resource_path('config/hs_negative.csv')
    hs_negative_df = pd.read_csv(csv_path)
    hs_negative_set = set(hs_negative_df)
    data_negative = input_file[input_file['HSCode'].isin(hs_negative_set)]

    return data_negative


# 通过align_hscode函数检查和调整HSCode字段。HSCode必须为6位数，超过6位的部分会被截断，不足6位则报错。
def align_hscode(input_file):
    # 检查 HSCode
    if 'HSCode' not in input_file.columns:
        raise HscodeError("Input file must contain 'HSCode' column.")

    aligned_hscodes = []

    for hscode in input_file['HSCode']:
        if len(hscode) > 6:
            aligned_hscodes.append(hscode[:6])
        elif len(hscode) < 6:
            raise HscodeError(f"HSCode '{hscode}' is less than six digits.")
        else:
            aligned_hscodes.append(hscode)

    input_file['HSCode'] = aligned_hscodes
    return input_file

def truncate_hscode(split_group):
    # 检查 HSCode
    if 'HSCode' not in split_group:
        raise HscodeError("Input file must contain 'HSCode' column.")

    def validate_and_truncate(hscode):
        if len(hscode) >= 6:
            return hscode[:6]
        else:
            raise HscodeError(f"HSCode '{hscode}' is less than six digits.")

    # 更新原列
    split_group['HSCode'] = split_group['HSCode'].apply(validate_and_truncate)
    return split_group

def process_manifests(input_file, input_file_path):
    split_columns = ['TrackingNumber', 'IOSS']

    # 获取文件名并构建新的输出目录
    base_filename = os.path.splitext(os.path.basename(input_file_path))[0]  # 去掉扩展名
    output_directory = os.path.join(os.path.dirname(input_file_path), base_filename)
    os.makedirs(output_directory, exist_ok=True)  # 创建新文件夹

    # Create over150 directory if it doesn't exist
    over150_directory = os.path.join(output_directory, 'over150')
    os.makedirs(over150_directory, exist_ok=True)

    under150_groups = []

    grouped = input_file.groupby(split_columns)
    input_file['Total Price'] = pd.to_numeric(input_file['Total Price'], errors='coerce').fillna(0)
    for idx, (group_keys, group_df) in enumerate(grouped):
        # Ensure 'IOSS' column is not null
        group_df['IOSS'] = group_df['IOSS'].fillna('Unknown')

        # Check and split if necessary
        split_groups = []
        while not group_df.empty:
            valid_chunk = group_df.head(999)
            split_groups.append(valid_chunk)
            group_df = group_df[~group_df.index.isin(valid_chunk.index)]

        for split_group in split_groups:
            total_price = split_group['Total Price'].sum()
            ioss_value = split_group['IOSS'].iloc[0]

            if total_price > 150:
                filename = f"Over150_{split_columns[0]}_{split_group[split_columns[0]].iloc[0]}.xlsx"
                output_path = os.path.join(over150_directory, filename)
                split_group.to_excel(output_path, index=False)
            else:
                try:
                    truncate_hscode(split_group)
                except HscodeError as e:
                    self.show_error(e.__str__())
                    return False
                under150_groups.append(split_group)
                # Get the first row's split_column values for naming
                split_name_values = f"{split_columns[0]}_{split_group[split_columns[0]].iloc[0]}"
                folder_name = f"IOSS_{ioss_value}"
                folder_path = os.path.join(output_directory, folder_name)

                # Create folder if not exists
                os.makedirs(folder_path, exist_ok=True)

                # Save file
                output_file_name = f"{split_name_values}.xlsx"
                output_path = os.path.join(folder_path, output_file_name)
                split_group.to_excel(output_path, index=False)

    return under150_groups
