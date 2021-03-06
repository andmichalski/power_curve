import glob

import matplotlib.pyplot as plt
import numpy as np

import fitdecode
import pandas as pd


class Parser:

    def get_files(self, directory='data'):
        return glob.glob(directory + '/*.fit')

    def collect_data(self):
        file_list = self.get_files()
        output_df = None
        for filename in file_list:
            df = self.create_dataframe(filename)
            if output_df is None:
                output_df = df
            else:
                output_df.append(df)
        return output_df

    def create_dataframe(self, filename='bike.fit'):
        with fitdecode.FitReader(filename) as fit:
            data = []
            columns = ['timestamp', 'distance_m', "accumulated_power_w", "enhanced_speed_m_s",
                       "speed_m_s", "power_w", "heart_rate_bpm", "cadence_rpm", "temperature_c",
                       "fractional_cadence_rpm",
                       ]
            field_map = ['timestamp', 'distance', 'accumulated_power', 'enhanced_speed',
                         'speed', 'power', 'heart_rate', 'cadence', 'temperature', 'fractional_cadence']

            for frame in fit:
                if isinstance(frame, fitdecode.FitDataMessage):
                    if frame.name == "record":
                        row = list(range(10))

                        for field in frame.fields:
                            if field.name in field_map:
                                row[field_map.index(field.name)] = field.value
                                # row.append(field.value)

                        data.append(row)
            if len(data[-1]) == 10:
                dataset = pd.DataFrame(data=data, columns=columns)
                return dataset
            else:
                return None

    def find_velocity(self, average_power, df):
        df.sort_values(by=['speed_m_s'])

        df['speed_km_h'] = df['speed_m_s'] * (3600/1000)
        df = df[df['power_w'] > 1.0]

        p = np.poly1d(np.polyfit(df['power_w'], df['speed_km_h'], 2))
        average_velocity = p(average_power)
        return average_velocity

    def find_distance(self, velocity, time_hh_mm_ss):
        splitted_time = time_hh_mm_ss.split(":")
        hours = float(splitted_time[0])
        minutes = float(splitted_time[1])
        seconds = float(splitted_time[2])
        distance = velocity * (hours + (minutes / 60.0) + (seconds / 3600.0))
        return distance

    def show_plot(self, df):
        df.sort_values(by=['speed_m_s'])
        df['speed_km_h'] = df['speed_m_s'] * (3600/1000)

        df = df[df['power_w'] > 1.0]

        p = np.poly1d(np.polyfit(df['speed_km_h'], df['power_w'], 2))

        speed = np.linspace(0, 50, 501)
        plt.plot(speed, p(speed))
        plt.xlabel('Speed [km/h]')
        plt.ylabel('Power [W]')
        plt.ylim(ymin=0)
        plt.xlim(xmin=0)
        plt.grid(which="both", axis='both')

        plt.show()


if __name__ == "__main__":
    parser = Parser()
    df = parser.collect_data()
    # show_plot(df)

    input_power = input('Type average power: ')
    average_power = int(input_power)

    input_time = input('Type time of effort [hh:mm:ss]: ')

    average_velocity = parser.find_velocity(average_power, df)

    distance = parser.find_distance(average_velocity, input_time)
    print(f'Distance is {distance:.2f} km')
