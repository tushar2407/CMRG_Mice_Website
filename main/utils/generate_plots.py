from django.conf import settings
MEDIA_ROOT = settings.MEDIA_ROOT

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime, timedelta
import re
import matplotlib.dates as mdates
import matplotlib.patches as patches
import warnings
import matplotlib.lines as mlines
import numpy as np
import pandas as pd
import math


from main.utils.base import group_to_sheet, group_to_mice, book, group_to_control_mice

warnings.filterwarnings("ignore")

path_to_files = [
    r"/home/ubuntu/Group_6_3_19_2024",
    r"/home/ubuntu/Group_6",
    r"/home/ubuntu/Group6_7"
    # r"/Users/tush/Library/CloudStorage/GoogleDrive-tushar.mohan2001@gmail.com/Other computers/My Laptop (1)/Group_6",
    # r"/Users/tush/Library/CloudStorage/GoogleDrive-tushar.mohan2001@gmail.com/Other computers/My Laptop (1)/Group6_7"
]
control_mice = []


plt.rcParams.update(plt.rcParamsDefault)

def extract_mouse_data_cleaned(df, mouse_id):
    # print(f"Processing data for mouse ID: {mouse_id}")
    # print(df.head())
    if mouse_id not in df.columns:
        return None, None, None

    weight_lifting_col = df.columns[df.columns.get_loc(mouse_id) + 1]
    remaining_pellets_col = df.columns[df.columns.get_loc(weight_lifting_col) + 1]

    # print([1, df.columns.index(mouse_id), df.columns.index(weight_lifting_col), df.columns.index(remaining_pellets_col)])
    # Extract data for the specific mouse
    mouse_data = df[['Unnamed: 1', mouse_id, weight_lifting_col, remaining_pellets_col]]
    # print(f"Cleaned data for {mouse_id}:")
    # print(mouse_data.head())

    # Clean data: Convert non-numeric entries to None for relevant columns
    mouse_data[mouse_id] = pd.to_numeric(mouse_data[mouse_id], errors='coerce')
    mouse_data[weight_lifting_col] = pd.to_numeric(mouse_data[weight_lifting_col], errors='coerce')
    mouse_data[remaining_pellets_col] = pd.to_numeric(mouse_data[remaining_pellets_col], errors='coerce')
    # print("Cleaned data:", mouse_data.head())

    # Drop rows where the "Unnamed: 1" column (assumed to be Date) is missing
    mouse_data = mouse_data.dropna(subset=['Unnamed: 1'])

    # Rename columns for clarity
    mouse_data.columns = ['Date', 'Body Mass', 'Weight Lifting', 'Remaining Pellets']

    # Convert dates to string format
    mouse_data['Date'] = pd.to_datetime(mouse_data['Date']).dt.strftime('%m/%d/%y')



    # Convert data to dictionaries for easy access
    mouse_mass_data = dict(zip(mouse_data['Date'], mouse_data['Body Mass']))
    # print(mouse_mass_data)
    weight_lifted_data = dict(zip(mouse_data['Date'], mouse_data['Weight Lifting']))
    # print(mouse_id, weight_lifted_data)
    # input()
    remaining_pellets_data = dict(zip(mouse_data['Date'], mouse_data['Remaining Pellets']))

    # print("Mouse Mass Data:", mouse_mass_data)
    # print("Weight Lifted Data:", weight_lifted_data)
    # print("Remaining Pellets Data:", remaining_pellets_data)

    # print(f"Extracted and cleaned data for {mouse_id}:")
    # print(f"Final mouse {mouse_id}")
    # print(mouse_mass_data)
    # print(weight_lifted_data)
    # print(remaining_pellets_data)

    return mouse_mass_data, weight_lifted_data, remaining_pellets_data


def parse_mouse_data(mouse_data):
    # print(f"Parsing mouse data: {mouse_data}")
    mouse_mass_data = {}
    weight_lifted_data = {}

    for entry in mouse_data:
        date_str, mass_str, weight_str = entry.strip('()').split(', ')
        date = datetime.strptime(date_str, '%m/%d/%y').strftime('%m/%d/%y')

        mass = float(mass_str.split(' ')[0])
        weight_lifted = float(weight_str.split(' ')[0])

        mouse_mass_data[date] = mass
        weight_lifted_data[date] = weight_lifted

    return mouse_mass_data, weight_lifted_data


def format_date(date_str):
    date = datetime.strptime(date_str, '%m/%d/%y')
    return date.strftime('%a %b %d')


def extract_data_for_file(file_keyword, path_to_files, start_date):
    # print(f"Extracting data for file keyword: {file_keyword}")
    day_lift_data = {}
    night_lift_data = {}
    day_reward_data = {}
    night_reward_data = {}
    for path in path_to_files:
        for file_name in os.listdir(path):
            if file_keyword in file_name:
                with open(os.path.join(path, file_name), 'r', encoding='utf-8', errors='ignore') as file:
                    lines = file.readlines()

                    end_date_match = re.search(r"End Date: (\d{2}/\d{2}/\d{2})", ''.join(lines))
                    lift_match = re.search(r"L:\s+([\d.]+)", ''.join(lines))
                    reward_match = re.search(r"R:\s+([\d.]+)", ''.join(lines))

                    if end_date_match and lift_match and reward_match:
                        # print(end_date_match)
                        date_str = end_date_match.group(1)
                        date = datetime.strptime(date_str, '%m/%d/%y')
                        print(file_keyword, date)
                        if date <= start_date - timedelta(1):
                            continue

                        lift_value = float(lift_match.group(1))
                        reward_value = float(reward_match.group(1))

                        if "Night" in file_name:
                            previous_date = date - timedelta(days=1)
                            previous_date_str = previous_date.strftime('%m/%d/%y')

                            night_lift_data[previous_date_str] = lift_value
                            night_reward_data[previous_date_str] = reward_value
                        elif "Day" in file_name:
                            day_lift_data[date_str] = lift_value
                            day_reward_data[date_str] = reward_value

    for date in night_lift_data:
        if date not in day_lift_data:
            day_lift_data[date] = 0
            day_reward_data[date] = 0

    print(f"Extracted day lift data for {file_keyword}:")
    print(day_lift_data)
    # print(f"Extracted night lift data for {file_keyword}:")
    # print(night_lift_data)
    # print(f"Extracted day reward data for {file_keyword}:")
    # print(day_reward_data)
    # print(f"Extracted night reward data for {file_keyword}:")
    # print(night_reward_data)

    return day_lift_data, night_lift_data, day_reward_data, night_reward_data


def updated_plot_and_display(df, file_keyword, y_limit, ax1, ax2, path_to_files, start_date, Specimen_No, mouse_mass_data, weight_lifted_data, remaining_pellets_data):    # Extract data for each time period (day/night) and each metric (lift/reward)
    # print(f"Generating plot for keyword: {file_keyword}")
    day_lift_data, night_lift_data, day_reward_data, night_reward_data = extract_data_for_file(file_keyword, path_to_files, start_date)

    # Prepare the list of dates for plotting
    dates = list(set(day_lift_data.keys()).union(set(night_lift_data.keys())))[:]   
    dates = [datetime.strptime(date, '%m/%d/%y') for date in dates]

    # Sort the datetime objects
    sorted_dates = sorted(dates)

    # Convert sorted datetime objects back to date strings
    dates = [date.strftime('%m/%d/%y') for date in sorted_dates]

    formatted_dates = [format_date(date) for date in dates]
    date_indices = list(range(len(dates)))

    # Calculate combined values for lifts and rewards
    combined_lift_values = [day_lift_data.get(date, 0) + night_lift_data.get(date, 0) for date in dates]
    combined_reward_values = [day_reward_data.get(date, 0) + night_reward_data.get(date, 0) for date in dates]

    for i, date_str in enumerate(dates):
        # print(f"Plotting data for date {date_str}: Index={date_indices[i]}, Lift={combined_lift_values[i]}, Reward={combined_reward_values[i]}")
        date = datetime.strptime(date_str, '%m/%d/%y')
        if date.weekday() == 0 or date.weekday() == 4:
            ax1.axvspan(i - 0.5, i + 0.5, color='#87CEEB', alpha=0.3)
            ax2.axvspan(i - 0.5, i + 0.5, color='#87CEEB', alpha=0.3)
        elif date.weekday() == 2:
            ax1.axvspan(i - 0.5, i + 0.5, color='#FF9B8A', alpha=0.3)
            ax2.axvspan(i - 0.5, i + 0.5, color='#FF9B8A', alpha=0.3)

    width = 0.9

    modified_values = []

    for i, date_str in enumerate(dates):
        date = datetime.strptime(date_str, '%m/%d/%y')

        remaining_pellets = remaining_pellets_data[file_keyword].get(date_str, 0)
        
        # Check if remaining_pellets is NaN and replace it with 0
        if np.isnan(remaining_pellets):
            remaining_pellets = 0
        
        if date.weekday() == 0 or date.weekday() == 4:
            modified_value = combined_reward_values[i] + 250 - remaining_pellets
        else:
            modified_value = combined_reward_values[i]
        
        modified_values.append(modified_value)

    # Plotting lifts and rewards with day/night distinction and total values
    max_lift = 0
    max_reward = 0
    for i, date_str in enumerate(dates):
        date = datetime.strptime(date_str, '%m/%d/%y')
        formatted_date = date.strftime('%m/%d/%y')

        lift_val_day = day_lift_data.get(formatted_date, 0)
        lift_val_night = night_lift_data.get(formatted_date, 0)
        reward_val_day = day_reward_data.get(formatted_date, 0)
        reward_val_night = night_reward_data.get(formatted_date, 0)
        modified_value = modified_values[i]
        combined_lift_val = lift_val_day + lift_val_night
        combined_reward_val = reward_val_day + reward_val_night

        max_lift = max(max_lift, combined_lift_val)
        max_reward = max(max_reward, combined_reward_val)

        ax1.bar(date_indices[i], lift_val_night, width=0.9, color='white', edgecolor='black', label="Night" if i == 0 else "")
        ax1.bar(date_indices[i], lift_val_day, width=0.9, color='gray', edgecolor='black', bottom=lift_val_night, label="Day" if i == 0 else "")
        ax1.text(date_indices[i], combined_lift_val + 5, f"{int(combined_lift_val)}", ha='center', va='bottom', fontsize=7, color='black', rotation=0)
        
        if formatted_date in ['01/12/24', '01/15/24','11/27/23', '12/01/23']:
        # Only blue bars for these specific dates
            ax2.bar(date_indices[i], modified_value, width=0.9, color='lightsteelblue', edgecolor='black', label="Day" if i == 0 else "")
            ax2.text(date_indices[i], modified_value + 5, f"{int(modified_value)}", ha='center', va='bottom', fontsize=6, color='black', rotation=0)
            ax2.text(date_indices[i], combined_reward_val + 5, f"{int(combined_reward_val)}", ha='center', va='bottom', fontsize=6, color='black', rotation=0)
            ax2.text(date_indices[i], combined_reward_val + 5, f"{int(combined_reward_val)}", ha='center', va='bottom', fontsize=6, color='black', rotation=0)

        else:
            # Check if it's Monday or Friday to use modified_value, else use combined_reward_val
            if date.weekday() == 0 or date.weekday() == 4:
                if modified_value <= 200:
                    ax2.bar(date_indices[i], modified_value, width=0.9, color='lightsteelblue', edgecolor='black', bottom=reward_val_night, label="Day" if i == 0 else "")
                    ax2.bar(date_indices[i], reward_val_night, width=0.9, color='white', edgecolor='black', label="Night" if i == 0 else "")
                    ax2.bar(date_indices[i], reward_val_day, width=0.9, color='gray', edgecolor='black', bottom=reward_val_night, label="Day" if i == 0 else "")
                else:
                    ax2.bar(date_indices[i], 200, width=0.9, color='lightsteelblue', edgecolor='black', label="Day" if i == 0 else "")
                    # ax2.bar(date_indices[i], modified_value - 200, width=0.9, color='black', edgecolor='black', bottom=200, label="Day" if i == 0 else "")
                    ax2.bar(date_indices[i], reward_val_night, width=0.9, color='white', edgecolor='black', label="Night" if i == 0 else "")
                    ax2.bar(date_indices[i], reward_val_day, width=0.9, color='gray', edgecolor='black', bottom=reward_val_night, label="Day" if i == 0 else "")
                ax2.text(date_indices[i], modified_value + 5, f"{int(modified_value)}", ha='center', va='bottom', fontsize=6, color='black', rotation=0)
                ax2.text(date_indices[i], combined_reward_val + 5, f"{int(combined_reward_val)}", ha='center', va='bottom', fontsize=6, color='black', rotation=0)

            else:
                ax2.bar(date_indices[i], reward_val_night, width=0.9, color='white', edgecolor='black', label="Night" if i == 0 else "")
                ax2.bar(date_indices[i], reward_val_day, width=0.9, color='gray', edgecolor='black', bottom=reward_val_night, label="Day" if i == 0 else "")
                ax2.text(date_indices[i], combined_reward_val + 5, f"{int(combined_reward_val)}", ha='center', va='bottom', fontsize=6, color='black', rotation=0)


    # Setting axes labels, ticks, and grid
    ax1.set_xticks(date_indices)
    ax1.set_xticklabels(formatted_dates, rotation=45, ha='right', fontsize=8)
    ax1.set_ylabel('Lifts', fontsize=16)
    ax1.set_ylim(0, max(200, max_lift + 10))

    ax2.set_xticks(date_indices)
    ax2.set_xticklabels(formatted_dates, rotation=45, ha='right', fontsize=8)
    ax2.set_ylabel('Rewards', fontsize=16)
    ax2.set_ylim(0, max(500, max_reward + 10))

    # Additional y-axes for mouse mass and weight lifted
    ax3 = ax2.twinx()
    ax4 = ax1.twinx()

    y_ticks = ax2.get_yticks()
    x_ticks = ax1.get_xticks()
    # if Specimen_No == Female_Lifters:
    y_ticks = [tick for tick in y_ticks if tick % 200 == 0] + [165] + [200]
    x_ticks = [tick for tick in x_ticks if tick % 200 == 0]
    ax2.set_yticks(y_ticks)

    # Extracting and plotting control mice mass data only for available dates
    for control_mouse in control_mice:
        control_mouse_mass_data, _, _ = extract_mouse_data_cleaned(df, control_mouse)
        print(f"Control Mouse Data for {control_mouse}:")
        try:
            # Assuming control_mouse_mass_data is a dictionary with numerical values
            current_max = max(control_mouse_mass_data.values(), default=0)
        except:
            continue
        # Convert 'dates' to 'YYYY-MM-DD' format
        dates_converted = [datetime.strptime(date, '%m/%d/%y').strftime('%m/%d/%y') for date in dates]
        # Create list of tuples (date index, mass value) for plotting
        plot_data = [(date_index, control_mouse_mass_data[date]) for date, date_index in zip(dates_converted, date_indices) if date in control_mouse_mass_data and control_mouse_mass_data[date] is not None]
        
        # Separate the tuples into x (date indices) and y (mass values)
        x_values, y_values = zip(*plot_data) if plot_data else ([], [])
        # Plot Control Mouse Mass data as light gray dots
        ax3.scatter(x_values, y_values, color='0.7', s=50, label=f'Control {control_mouse} Mass (g)', marker='*', zorder=2)


    mouse_mass_values = [mouse_mass_data.get(date, None) for date in dates]
    # print("Mouse_mass_values", mouse_mass_values)
    date_indices_filtered = [date_indices[i] for i, value in enumerate(mouse_mass_values) if value is not None]
    # print("date_indices_filtered", len(date_indices_filtered))
    mouse_mass_values_filtered = [value for value in mouse_mass_values if value is not None]

    # Converting the list to a pandas Series for interpolation
    mouse_mass_series = pd.Series(mouse_mass_values_filtered)

    # Interpolating missing values
    mouse_mass_values_interpolated = mouse_mass_series.interpolate()

    # Converting back to list for display
    mouse_mass_values_interpolated = mouse_mass_values_interpolated.tolist()

    # Plot Mouse Mass data with connected dots and no marker for interpolated points
    ax3.plot(date_indices_filtered, mouse_mass_values_filtered, label='Mouse Mass (g)', color='green', marker='o', linestyle='-')
    ax3.plot(date_indices_filtered, mouse_mass_values_interpolated, color='green', linestyle='-')
    ax3.set_ylabel('Body Mass (g)', fontsize=16, color='green')
    ax3.set_ylim(10, 27)

    # Preprocess Weight Lifted data (similar to Mouse Mass)
    weight_lifted_values = [weight_lifted_data.get(date, None) for date in dates]
    weight_lifted_values_filtered = [value for value in weight_lifted_values if value is not None]
    
    weight_lifted_values_interpolated = np.interp(date_indices, date_indices_filtered, weight_lifted_values_filtered)


    weight_lifted_values_wo_nan = list(weight_lifted_data.values())
    if any(math.isnan(value) or math.isinf(value) for value in weight_lifted_values_wo_nan):
        # Replace NaN or Inf values with zeros
        weight_lifted_values_wo_nan = [0 if math.isnan(value) or math.isinf(value) else value for value in weight_lifted_values]
        print(weight_lifted_values_wo_nan)

    # Plot Weight Lifted data with connected dots and no marker for interpolated points
    ax4.plot(date_indices_filtered, weight_lifted_values_filtered, label='Weight Lifted (g)', color='red', marker='x', linestyle='-')
    ax4.plot(date_indices, weight_lifted_values_interpolated, color='red', linestyle='-')
    ax4.set_ylabel('Weight Lifted (g)', fontsize=16, color='red')
    ax4.set_ylim(0, max(weight_lifted_values_wo_nan, default=0) + 10)


    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    # Titles and tick settings
    ax1.set_title(file_keyword, fontsize=14, fontweight='bold')
    ax2.set_title(file_keyword, fontsize=14, fontweight='bold')
    ax1.tick_params(axis='both', labelsize=14)
    ax2.tick_params(axis='both', labelsize=14)
    ax3.tick_params(axis='y', labelsize=14)
    ax4.tick_params(axis='y', labelsize=14)

    # print(f"Completed plotting for {file_keyword}")


def generate_plots(Specimen_No, sheet_name, group, start_date_str='2023-11-27'):
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

    try:
        # df = pd.read_excel(file_path, sheet_name=sheet_name)
        worksheet = book.worksheet(sheet_name)
        # Get all values from the worksheet
        table = worksheet.get_all_values()
        
        for i in range(len(table[0])):
            if table[0][i]=='':
                table[0][i] = "Unnamed: " + str(i)

        # Convert table data into a pandas DataFrame
        df = pd.DataFrame(table[1:], columns=table[0])
        # print(df)
        # df = pd.read_excel(file_path, sheet_name=sheet_name)
    except Exception as e:
        raise Exception(f"Error loading Excel file: {str(e)}")


    max_y_limit = 0
    # Initialize mouse_data_dict
    mouse_data_dict = {}

    remaining_pellets_data = {}

    weight_lifted_data = {}

    for mouse_id in Specimen_No:
        # Now unpacking three values
        mouse_mass_data, weight_lifted_data_temp, pellets_data = extract_mouse_data_cleaned(df, mouse_id)

        if weight_lifted_data == {}:
            weight_lifted_data = weight_lifted_data_temp
        
        remaining_pellets_data[mouse_id] = pellets_data
        # Convert data to the required format
        mouse_data_dict[mouse_id] = [
            f"({date}, {mass} g, {weight} g)"
            for date, mass, weight in zip(mouse_mass_data.keys(), mouse_mass_data.values(), weight_lifted_data.values())
            if datetime.strptime(date, '%m/%d/%y') >= start_date
        ]

    for keyword in Specimen_No:
        active_lift_data, inactive_lift_data, active_reward_data, inactive_reward_data = extract_data_for_file(keyword, path_to_files, start_date)
        y_limit = max(max(active_lift_data.values(), default=0), max(inactive_lift_data.values(), default=0),
                      max(active_reward_data.values(), default=0), max(inactive_reward_data.values(), default=0)) + 10
        max_y_limit = max(max_y_limit, y_limit)
    
    with PdfPages(f'{MEDIA_ROOT}/Female_lifters_{group}.pdf') as pdf:
        print("pdf created")
        for i in range(0, len(Specimen_No), 4):
            specimens = Specimen_No[i:i + 4]
            print(specimens)
            for i, keyword in enumerate(specimens):
                print(keyword)
                if i % 4 == 0:
                    fig, axs = plt.subplots(4, 2, figsize=(20, 15))
                    print("Here")
                    
                    plt.figtext(0.5, 1.05, "Female Lifters", ha="center", va="center", fontsize=30, fontweight='bold')                    
                    plt.figtext(0.25, 1.02, "Lifts", ha="center", va="center", fontsize=25, fontweight='bold')
                    plt.figtext(0.64, 1.02, "Rewards", ha="center", va="center", fontsize=25, fontweight='bold')
                ax1 = axs[i % 4, 0]
                ax2 = axs[i % 4, 1]

                # Extracting mouse data for the current mouse ID
                mouse_data = mouse_data_dict[keyword]
                print(mouse_data)
                mouse_mass_data, weight_lifted_data = parse_mouse_data(mouse_data)

                updated_plot_and_display(df, keyword, max_y_limit, ax1, ax2, path_to_files, start_date, specimens, mouse_mass_data, weight_lifted_data, remaining_pellets_data)

                plt.subplots_adjust(hspace=0.6, wspace=0.3)
                # Add the following lines to increase the xtick label font size
                ax1.tick_params(axis='x', labelsize=9)
                ax2.tick_params(axis='x', labelsize=9)
                plt.tight_layout(pad=1.0)

            common_legend_labels = ["Day", "Night", "Rest", "Weights Added"]
            common_legend_colors = ['white', 'gray', '#87CEEB', '#FF9B8A']
            common_legend_patches = [patches.Patch(facecolor=color, edgecolor='black', linewidth=1.2, label=label) for color, label in zip(common_legend_colors, common_legend_labels)]
            common_legend_ax = fig.add_subplot(111, frameon=False)
            common_legend_ax.axis('off')
            common_legend_ax.legend(handles=common_legend_patches, loc='upper left', bbox_to_anchor=(0.36, 1.08), ncol=2, fontsize=20, handlelength=1, handletextpad=0.1)
            # Additional legend for Control Body Mass
            lifts_legend_labels = ["Weight Lifted"]
            lifts_legend_colors = ['red']
            lifts_legend_patches = [patches.Patch(facecolor=color, edgecolor='black', linewidth=1.2, label=label) for color, label in zip(lifts_legend_colors, lifts_legend_labels)]
            dotted_legend_label = "4.0 g rest day pellets"
            dotted_legend_line = mlines.Line2D([], [], color='black', linestyle='--', linewidth=1.2, label=dotted_legend_label, markerfacecolor='red', markersize=10, markeredgecolor='black')        
            all_legend_handles = lifts_legend_patches + [dotted_legend_line]
            # .legend(handles=all_legend_handles, loc='upper left', bbox_to_anchor=(-0.05, 1.12), fontsize=20, handlelength=1, handletextpad=0.1)               # lifts_body_mass_patch = patches.Patch(facecolor='0.7', edgecolor='black', linewidth=1.2, label='Control Body Mass')
            lifts_legend_ax = fig.add_subplot(111, frameon=False)
            lifts_legend_ax.axis('off')
            lifts_legend_ax.legend(handles=all_legend_handles, loc='upper left', bbox_to_anchor=(-0.05, 1.12), fontsize=20, handlelength=1, handletextpad=0.1)
            rewards_legend_labels = ["Body Mass", "Control Body Mass", "Rest Day Pellets", "No of extra Pellets"]
            rewards_common_legend_colors = ['green', '0.7', 'lightsteelblue', 'black']
            rewards_common_legend_patches = [patches.Patch(facecolor=color, edgecolor='black', linewidth=1.2, label=label) for color, label in zip(rewards_common_legend_colors, rewards_legend_labels)]
            rewards_common_legend_ax = fig.add_subplot(111, frameon=False)
            rewards_common_legend_ax.axis('off')
            rewards_common_legend_ax.legend(handles=rewards_common_legend_patches, loc='upper left', bbox_to_anchor=(0.69, 1.12), ncol=2, fontsize=20, handlelength=1, handletextpad=0.1)
            pdf.savefig(fig, bbox_inches='tight')
            plt.show()
            plt.close(fig)

# generate_plots(Female_Lifters, '2023-11-27')

def trigger_generate_plots(data):
    global control_mice
    control_mice = group_to_control_mice[data['group']]

    generate_plots(
        group_to_mice[data['group']],
        group_to_sheet[data['group']],
        data['group']
    )