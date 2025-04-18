import os
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import glob
import shutil

SCHEMES = ["cubic", "bbr", "vegas"]

PROFILES = {
    "A": {
        "delay": 5,
        "downlink": "mahimahi/traces/TMobile-LTE-driving.down",
        "uplink": "mahimahi/traces/TMobile-LTE-driving.up"
    },
    "B": {
        "delay": 200,
        "downlink": "mahimahi/traces/TMobile-LTE-short.down",
        "uplink": "mahimahi/traces/TMobile-LTE-short.up"
    }
}


def run_experiments():
    for profile, config in PROFILES.items():
        print(f"\n=== Running experiments for Profile {profile} ===")
        for scheme in SCHEMES:
            out_dir = f"results/profile_{profile}/{scheme}"
            os.makedirs(out_dir, exist_ok=True)

            cmd = (
                f"mm-delay {config['delay']} "
                f"mm-link {config['downlink']} {config['uplink']} -- "
                f"bash -c 'python3 tests/test_schemes.py --schemes \"{scheme}\" > {out_dir}/log.txt 2>&1'"
            )

            try:
                subprocess.run(cmd, shell=True, check=True)
                print(f"[✓] Completed {scheme} on profile {profile}")
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] {scheme} failed on Profile {profile}: {e}")

            # After running, move latest CSV from logs/ to results/
            metric_files = sorted(glob.glob(f"logs/metrics_{scheme}_*.csv"), key=os.path.getmtime, reverse=True)
            if metric_files:
                latest_metric = metric_files[0]
                dest_path = os.path.join(out_dir, f"{scheme}_cc_log.csv")
                shutil.copy(latest_metric, dest_path)
            else:
                print(f"[!] No metric CSV found for {scheme} in profile {profile}")


def parse_logs():
    all_dfs = []
    for profile in PROFILES:
        for scheme in SCHEMES:
            src_path = f'results/profile_{profile}/{scheme}/{scheme}_cc_log.csv'
            if os.path.exists(src_path):
                df = pd.read_csv(src_path)
                df['scheme'] = scheme
                df['profile'] = profile
                df['timestamp'] = range(len(df))  # Simulated time axis
                all_dfs.append(df)
            else:
                print(f"[!] Missing log for {scheme} in profile {profile}")
    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()


def plot_throughput_time_series(df):
    for profile in df['profile'].unique():
        plt.figure()
        for scheme in df['scheme'].unique():
            subdf = df[(df["scheme"] == scheme) & (df["profile"] == profile)]
            plt.plot(subdf['timestamp'], subdf['throughput'], label=scheme)
        plt.title(f'Throughput vs Time (Profile {profile})')
        plt.xlabel('Time (s)')
        plt.ylabel('Throughput (Mbps)')
        plt.legend()
        plt.grid()
        plt.savefig(f'graphs/throughput_profile_{profile}.png')
        plt.close()


def plot_loss_time_series(df):
    for profile in df['profile'].unique():
        plt.figure()
        for scheme in df['scheme'].unique():
            subdf = df[(df["scheme"] == scheme) & (df["profile"] == profile)]
            if 'loss_rate' in subdf.columns:
                plt.plot(subdf['timestamp'], subdf['loss_rate'], label=scheme)
        plt.title(f'Loss Rate vs Time (Profile {profile})')
        plt.xlabel('Time (s)')
        plt.ylabel('Loss Rate')
        plt.legend()
        plt.grid()
        plt.savefig(f'graphs/loss_profile_{profile}.png')
        plt.close()


def plot_rtt_summary(df):
    summary = []
    for profile in df['profile'].unique():
        for scheme in df['scheme'].unique():
            subdf = df[(df["scheme"] == scheme) & (df["profile"] == profile)]
            if not subdf.empty:
                avg_rtt = subdf['rtt'].mean()
                p95_rtt = subdf['rtt'].quantile(0.95)
                summary.append((scheme, profile, avg_rtt, p95_rtt))
    summary_df = pd.DataFrame(summary, columns=['Scheme', 'Profile', 'Avg RTT', '95th RTT'])
    summary_df.to_csv('graphs/rtt_summary.csv', index=False)
    print(summary_df.to_string(index=False))


def plot_rtt_vs_throughput(df):
    plt.figure()
    for profile in df['profile'].unique():
        for scheme in df['scheme'].unique():
            subdf = df[(df["scheme"] == scheme) & (df["profile"] == profile)]
            if not subdf.empty:
                avg_rtt = subdf['rtt'].mean()
                avg_tp = subdf['throughput'].mean()
                plt.scatter(avg_rtt, avg_tp, label=f'{scheme}-{profile}')
                plt.annotate(f'{scheme}-{profile}', (avg_rtt, avg_tp))
    plt.title('Throughput vs RTT')
    plt.xlabel('RTT (ms)')
    plt.ylabel('Throughput (Mbps)')
    plt.grid()
    plt.legend()
    plt.savefig('graphs/rtt_vs_throughput.png')
    plt.close()


def main():
    os.makedirs('graphs', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    run_experiments()
    df = parse_logs()
    if df.empty:
        print('No logs found to process.')
        return
    plot_throughput_time_series(df)
    plot_loss_time_series(df)
    plot_rtt_summary(df)
    plot_rtt_vs_throughput(df)
    print('All experiments and graphs completed.')



if __name__ == '__main__':
    main()