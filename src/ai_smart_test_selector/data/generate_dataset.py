import numpy as np
import pandas as pd


MODULES = {
    "Clock": "Timing",
    "DMA": "Memory",
    "PCIe": "HighSpeedIO",
    "USB": "Connectivity",
    "Firmware": "Core",
    "Memory": "Memory",
    "Interrupt": "Core",
    "Cache": "Memory",
    "Boot": "Core",
}


def calculate_failure_risk(
    previous_fail_rate,
    flaky_score,
    code_churn,
    dependency_depth,
    firmware_version,
    environment,
):
    risk = (
        0.30 * previous_fail_rate
        + 0.20 * flaky_score
        + 0.20 * (code_churn / 100)
        + 0.15 * (dependency_depth / 10)
        + 0.10 * (firmware_version / 10)
    )

    if environment == "real_hw":
        risk += 0.10

    return min(risk, 1.0)


def generate_dataset(n=3000):

    data = []

    for i in range(n):

        module = np.random.choice(list(MODULES.keys()))
        subsystem = MODULES[module]

        firmware_version = np.random.randint(1, 15)
        hardware_revision = np.random.choice(["A", "B", "C"])

        test_type = np.random.choice(
            ["unit", "integration", "system"], p=[0.4, 0.35, 0.25]
        )

        execution_time_sec = np.random.randint(50, 1200)

        cpu_load = np.random.randint(10, 100)
        memory_usage = np.random.randint(100, 8000)
        io_activity = np.random.randint(1, 100)

        previous_fail_rate = np.random.uniform(0, 1)
        flaky_score = np.random.uniform(0, 1)

        code_churn_module = np.random.randint(0, 100)

        last_bug_age_days = np.random.randint(1, 365)

        dependency_depth = np.random.randint(1, 12)

        environment = np.random.choice(["emu", "real_hw"], p=[0.3, 0.7])

        risk = calculate_failure_risk(
            previous_fail_rate,
            flaky_score,
            code_churn_module,
            dependency_depth,
            firmware_version,
            environment,
        )

        failed = 1 if risk > 0.55 else 0

        data.append(
            [
                f"test_{i}",
                module,
                subsystem,
                firmware_version,
                hardware_revision,
                test_type,
                execution_time_sec,
                cpu_load,
                memory_usage,
                io_activity,
                previous_fail_rate,
                flaky_score,
                code_churn_module,
                last_bug_age_days,
                dependency_depth,
                environment,
                failed,
            ]
        )

    columns = [
        "test_id",
        "module",
        "subsystem",
        "firmware_version",
        "hardware_revision",
        "test_type",
        "execution_time_sec",
        "cpu_load",
        "memory_usage",
        "io_activity",
        "previous_fail_rate",
        "flaky_score",
        "code_churn_module",
        "last_bug_age_days",
        "dependency_depth",
        "environment",
        "failed",
    ]

    return pd.DataFrame(data, columns=columns)


if __name__ == "__main__":

    df = generate_dataset(3000)

    df.to_csv("src/ai_smart_test_selector/data/test_history.csv", index=False)

    print("dataset created")
