import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

import fitdecode
import pandas as pd
from sklearn.linear_model import LinearRegression


def create_df():
    with fitdecode.FitReader("bike.fit") as fit:
        data = []
        columns = ['timestamp', 'distance_m', "accumulated_power_w", "enhanced_speed_m_s",
                   "speed_m_s", "power_w", "heart_rate_bpm", "cadence_rpm", "temperature_c",
                   "fractional_cadence_rpm",
                   ]

        for frame in fit:
            # The yielded frame object is of one of the following types:
            # * fitdecode.FitHeader
            # * fitdecode.FitDefinitionMessage
            # * fitdecode.FitDataMessage
            # * fitdecode.FitCRC

            if isinstance(frame, fitdecode.FitDataMessage):
                # Here, frame is a FitDataMessage object.
                # A FitDataMessage object contains decoded values that
                # are directly usable in your script logic.

                if frame.name == "record":
                    row = []

                    for field in frame.fields:
                        row.append(field.value)

                    data.append(row)

        dataset = pd.DataFrame(data=data, columns=columns)

        return dataset


def find_velocity(average_power, df):
    df.sort_values(by=['speed_m_s'])
    df['speed_km_h'] = df['speed_m_s'] * (3600/1000)
    p = np.poly1d(np.polyfit(df['power_w'], df['speed_km_h'], 3))
    average_velocity = p(average_power)
    return average_velocity


def find_distance(velocity, time_hh_mm_ss):
    splitted_time = time_hh_mm_ss.split(":")
    hours = float(splitted_time[0])
    minutes = float(splitted_time[1])
    seconds = float(splitted_time[2])
    distance = velocity * (hours + (minutes / 60.0) + (seconds / 3600.0))
    return distance


def show_plot(df):
    df.sort_values(by=['speed_m_s'])
    df['speed_km_h'] = df['speed_m_s'] * (3600/1000)

    p = np.poly1d(np.polyfit(df['speed_km_h'], df['power_w'], 3))
    power = np.linspace(20, 40, 201)
    plt.plot(power, p(power))
    plt.show()


if __name__ == "__main__":
    dataset = create_df()
    input_power = input('Type average power: ')
    average_power = int(input_power)

    input_time = input('Type time of effort [hh:mm:ss]: ')

    average_velocity = find_velocity(average_power, dataset)

    distance = find_distance(average_velocity, input_time)
    print(f'Distance is {distance:.2f} km')
