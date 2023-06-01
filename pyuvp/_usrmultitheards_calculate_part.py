import threading


def calculate_y(x, y, index, lock):
    result = 2 * x - 1
    with lock:
        y[index] = result


def process_sequence(sequence):
    y = [None] * len(sequence)  # 创建与序列长度相同的空列表作为结果
    lock = threading.Lock()  # 创建线程锁用于同步输出顺序
    threads = []
    for i, x in enumerate(sequence):
        thread = threading.Thread(target=calculate_y, args=(x, y, i, lock))
        thread.start()
        threads.append(thread)

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    return y


# 序列
sequence = list(range(1000))

# 并行计算 y 序列
y_sequence = process_sequence(sequence)

print(y_sequence)
