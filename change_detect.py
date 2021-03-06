import matplotlib.pyplot as plt
import ruptures as rpt
import numpy as np
from sklearn.neighbors import KernelDensity
import scipy.stats as stats
from sklearn import metrics
import random


def make_kde(signal):
    bandwith = np.std(signal) * (4 / 3 / len(signal)) ** (1 / 5)
    return KernelDensity(kernel='gaussian', bandwidth=bandwith).fit(signal.reshape(-1, 1)), bandwith


def pre_process_signal(signal, signal_kde, trusted_kde):
    seg_score_signal = np.exp(signal_kde.score_samples(signal.reshape(-1, 1)))
    seg_score_trusted = np.exp(trusted_kde.score_samples(signal.reshape(-1, 1)))
    return np.absolute(seg_score_signal - seg_score_trusted)


if __name__ == "__main__":
    # generate the data
    # n = 2000
    # bkps = (/200, 400), (800, 1000), (1400, 1600)]
    # lower, upper = 0, 100
    # mu, sigma = 50, 25
    # X = stats.truncnorm((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)
    scores = []
    with open('scores.txt') as scores_file:
        for line in scores_file:
            if line:
                scores.append(float(line))
    scores = np.array(scores)
    scores_kde, _ = make_kde(scores)
    trusted_kde = scores_kde

    fingerprint = []
    with open('fingerprints.txt') as fingerprint_predictions:
        for line in fingerprint_predictions:
            if line:
                fingerprint.append(float(line))
    fingerprint_original = np.array(fingerprint)
    fingerprint_kde, _ = make_kde(fingerprint_original)

    data_x = []
    data_x_processed = []
    data_y = []
    n = 10000
    size = 200
    for i in range(0, n):
        cutoff = random.randint(50, size - 50)
        signal = scores_kde.sample(n_samples=cutoff * 2)
        signal = signal[(signal >= 0) & (signal <= 100)]
        signal = signal[0:cutoff]

        finger_count = size - cutoff
        fingerprint = fingerprint_kde.sample(n_samples=finger_count * 2)
        fingerprint = fingerprint[(fingerprint >= 0) * (fingerprint <= 10)]
        fingerprint = fingerprint[0:finger_count]
        fingerprint = (fingerprint * 2) + 80

        data = np.concatenate([signal, fingerprint])
        data_kde, _ = make_kde(data)
        data_processed = pre_process_signal(data, data_kde, trusted_kde)
        data_x.append(data)
        data_x_processed.append(data_processed)
        data_y.append(cutoff)

    data_y = np.array(data_y)
    predict_y = []
    predict_y_processed = []

    for i in range(0, n):
        algo = rpt.Pelt(model="rbf", min_size=25, jump=10).fit(data_x[i])
        my_bkps = algo.predict(pen=4.5)
        predict_y.append(my_bkps[0])
        algo = rpt.Pelt(model='rbf', min_size=3, jump=5).fit(data_x_processed[i])
        my_bkps = algo.predict(pen=2.95)
        predict_y_processed.append(my_bkps[0])
    predict_y = np.array(predict_y)
    predict_y_processed = np.array(predict_y_processed)
    print("Mean error")
    print(metrics.mean_absolute_error(data_y, predict_y))
    print("Mean error, processed")
    print(metrics.mean_absolute_error(data_y, predict_y_processed))

    # plot it
    # fig, axs = plt.subplots(1, 4)
    # fig.suptitle('Signal histograms')
    # axs[0].set_ylabel('Count')
    # axs[0].hist(trusted, bins=25, range=(0, 100))
    # axs[0].set_xlabel('Training signal')
    # axs[1].hist(signal_original, bins=25, range=(0, 100))
    # axs[1].set_xlabel('Legitimate signal\n(driver score)')
    # axs[2].hist(fingerprint, bins=25, range=(0, 100))
    # axs[2].set_xlabel('Malicious signal\n(driver fingerprint)')
    # axs[3].hist(signal, bins=25, range=(0, 100))
    # axs[3].set_xlabel('Combined\nmalicious\nand trusted')
    # ylim = int(plt.ylim()[1] // 100 + 1) * 100
    # print(ylim)
    # for a in axs:
    #     a.set_yticks(np.arange(0, 1100, step=100))
    # fig.align_labels()
    # plt.show()
    # x = np.array(range(0, n))
    # plt.plot(x, signal)
    # plt.title('Timeseries view of combined malicious and trusted signal')
    # plt.ylabel('Signal value')
    # plt.xlabel('Signal index')
    # plt.show()

    # preprocess with kde
    # trusted_kde, _ = make_kde(trusted)
    # sig_kde, _ = make_kde(signal)
    # error_sig = pre_process_signal(signal, sig_kde, trusted_kde)
    # error_sig_original = pre_process_signal(signal_original, sig_kde, trusted_kde)

    # find changepoints
    # model = "l1"  # "l1", "l2", or "rbf"
    # pen = 0.025  # seems to work well, TBD if it generalizes
    # n_bkps = 6
    # min_size = 3
    # jump = 5
    # ideally outputs all 6 changepoints defined above
    # print("KDE Processed with fingerprint data, Pelt")
    # algo = rpt.Pelt(model='rbf', min_size=min_size, jump=jump).fit(error_sig)
    # my_bkps = algo.predict(pen=2.95)
    # algo = rpt.Dynp(model=model, min_size=min_size, jump=jump).fit(error_sig)
    # my_bkps = algo.predict(n_bkps=n_bkps)
    # print(my_bkps)
    # ideally outputs nothing (well really [2000], by convention the library always ends with the length of the list)
    # print("KDE Processed without fingerprint data, Pelt")
    # algo = rpt.Pelt(model='rbf', min_size=min_size, jump=jump).fit(error_sig_original)
    # my_bkps = algo.predict(pen=2.95)
    # algo = rpt.Dynp(model=model, min_size=min_size, jump=jump).fit(error_sig_original)
    # my_bkps = algo.predict(n_bkps=n_bkps)
    # print(my_bkps)

    # print("KDE Processed with fingerprint data, Dynp")
    # algo = rpt.Dynp(model="l1", min_size=10, jump=jump).fit(error_sig)
    # my_bkps = algo.predict(n_bkps=n_bkps)
    # print(my_bkps)
    # print("Original signal without KDE Process, Dynp")
    # algo = rpt.Dynp(model="rbf", min_size=10, jump=jump).fit(signal)
    # my_bkps = algo.predict(n_bkps=n_bkps)
    # print(my_bkps)
    # print("Original signal without KDE Process, Pelt")
    # algo = rpt.Pelt(model="rbf", min_size=25, jump=10).fit(signal)
    # my_bkps = algo.predict(pen=4.5)
    # print(my_bkps)
    # print("Original signal without KDE Process, without fingerprint, Pelt")
    # algo = rpt.Pelt(model="rbf", min_size=25, jump=10).fit(signal_original)
    # my_bkps = algo.predict(pen=4.5)
    # print(my_bkps)
