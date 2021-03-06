import json

import matplotlib.pyplot as plt
import ruptures as rpt
import numpy as np
from sklearn.neighbors import KernelDensity
import scipy.stats as stats
from sklearn import metrics
import random
import scipy.signal as signal

if __name__ == "__main__":
    fingerprints = []
    with open('fingerprints.txt') as fingerprints_file:
        for line in fingerprints_file:
            if line:
                fingerprints.append(float(line))
    fingerprints = np.array(fingerprints)

    scores = []
    with open('scores.txt') as scores_file:
        for line in scores_file:
            if line:
                scores.append(float(line))
    scores = np.array(scores)

    # raw signals
    fig, axs = plt.subplots(1, 2)
    fig.suptitle('Signal histograms')
    axs[0].set_ylabel('Count')
    axs[0].hist(fingerprints)
    axs[0].set_xlabel('Fingerprints')
    axs[1].hist(scores)
    axs[1].set_xlabel('Scores')
    fig.align_labels()
    plt.show()

    # adjust scores and fingerprints to be between 0 and 1
    scores = (scores + 1) / 2
    fingerprints = ((fingerprints - 1) / 10)
    # make fingerprints in the same range as the scores
    fingerprints = fingerprints * 0.018 + 0.003

    # make kde of scores - need more data
    scores_kde = stats.gaussian_kde(scores)

    # make malicious signal - combine scores and fingerprints

    # only driver scores:
    # scores_chunk = scores_kde.resample(4000)[0]
    # scores_chunk = scores_chunk[(scores_chunk >= 0) & (scores_chunk <= 1)]
    # malicious = scores_chunk[0:2000]

    # fixed window malicious signal:
    # malicious = []
    # scores_chunk = scores_kde.resample(4000)[0]
    # scores_chunk = scores_chunk[(scores_chunk >= 0) & (scores_chunk <= 1)]
    # for i in range(0, 2000, 1000):
    #     malicious.append(scores_chunk[0:500])
    #     scores_chunk = scores_chunk[500:]
    #     fingerprints_choice = np.random.choice(len(fingerprints), 500)
    #     fingerprints_chunk = fingerprints[fingerprints_choice]
    #     fingerprints = np.delete(fingerprints, fingerprints_choice)
    #     malicious.append(fingerprints_chunk)
    # malicious = np.concatenate(malicious)

    # sampled randomly
    malicious = []
    # generate random changepoints then sort
    random_chunks = random.sample([i for i in range(1, 2000)], 2)  # only works correctly for even
    random_chunks.sort()
    print(random_chunks)
    random_chunks.insert(0, 0)
    random_chunks.insert(len(random_chunks), 2000)
    # print(random_chunks)
    # random_chunks = [0, 469, 582, 623, 746, 910, 1035, 1365, 1537, 1556, 1725, 2000]
    # print(random_chunks)
    scores_chunk = scores_kde.resample(4000)[0]
    scores_chunk = scores_chunk[(scores_chunk >= 0) & (scores_chunk <= 1)]
    for i in range(2, len(random_chunks), 2):
        scores_len = random_chunks[i - 1] - random_chunks[i - 2]
        malicious.append(scores_chunk[0:scores_len])
        scores_chunk = scores_chunk[scores_len:]
        fingerprint_len = random_chunks[i] - random_chunks[i - 1]
        fingerprints_choice = np.random.choice(len(fingerprints), fingerprint_len)
        fingerprints_added = fingerprints[fingerprints_choice]
        fingerprints = np.delete(fingerprints, fingerprints_choice)
        malicious.append(fingerprints_added)
    scores_len = random_chunks[len(random_chunks) - 1] - random_chunks[len(random_chunks) - 2]
    malicious.append(scores_chunk[0:scores_len])
    # malicious.append(scores_chunk[0:random_chunks[1]])
    # fingerprints_choice = np.random.choice(len(fingerprints), random_chunks[2] - random_chunks[1])
    # fingerprints_added = fingerprints[fingerprints_choice]
    # malicious.append(fingerprints_added)
    malicious = np.concatenate(malicious)

    # malicious.append(scores_chunk[0:1000])
    # fingerprints_choice = np.random.choice(len(fingerprints), 1000)
    # fingerprints_chunk = fingerprints[fingerprints_choice]
    # for i in range(0, 1000, 4):
    #     malicious.append(scores_chunk[i:(i+4)])
    #     malicious.append(fingerprints_chunk[i:(i+4)])
    # chunk = 200
    # chunks = 5
    # for i in range(0, chunks):
    #     scores_chunk = scores_kde.resample(chunk * 2)[0]
    #     scores_chunk = scores_chunk[(scores_chunk >= 0) & (scores_chunk <= 1)]
    #     malicious.append(scores_chunk[0:chunk])
    #     fingerprints_choice = np.random.choice(len(fingerprints), chunk)
    #     fingerprints_chunk = fingerprints[fingerprints_choice]
    #     fingerprints = np.delete(fingerprints, fingerprints_choice)
    #     malicious.append(fingerprints_chunk)
    # malicious = np.array(malicious)
    # malicious = np.concatenate(malicious)

    print(len(malicious))

    fig, axs = plt.subplots(1, 3)
    fig.suptitle('Adjusted signal histograms')
    axs[0].set_ylabel('Count')
    axs[0].hist(fingerprints)
    axs[0].set_xlabel('Fingerprints')
    axs[1].hist(scores)
    axs[1].set_xlabel('Scores')
    axs[2].hist(malicious)
    axs[2].set_xlabel('Malicious')
    fig.align_labels()
    plt.show()

    # fig, axs = plt.subplots(1, 2)
    plt.title('Scores distribution')
    plt.ylabel('Count')
    plt.hist(scores, bins=15)
    plt.xlabel('Scores')
    plt.show()

    plt.title('Resampled Scores distribution')
    plt.ylabel('Count')
    plt.hist(malicious, bins=20)
    plt.xlabel('Scores')
    plt.show()

    x = np.array(range(0, len(malicious)))
    plt.plot(x, malicious)
    plt.title('Timeseries view of legitimate signal')
    plt.ylabel('Signal value')
    plt.xlabel('Signal index')
    plt.show()

    # sp = np.fft.fft(malicious)
    # freq = np.fft.fftfreq(malicious.shape[-1])
    #
    # magnitude = np.sqrt(sp.real * sp.real + sp.imag * sp.imag)
    #
    # plt.plot(freq, magnitude)
    # plt.show()

    malicious = (malicious - malicious.mean()) / malicious.std()

    dataset = {'name': 'driver_scores_random2', 'longname': 'Driver Scores', 'n_obs': len(malicious), 'n_dim': 1}
    time = {'index': [i for i in range(0, len(malicious))]}
    dataset['time'] = time
    series = [{
        'label': 'Score',
        'type': 'float',
        'raw': [float('%.10f' % x) for x in malicious.tolist()]
    }]
    dataset['series'] = series
    with open('driver_scores_random2.json', 'w') as outfile:
        json.dump(dataset, outfile, indent=4)
