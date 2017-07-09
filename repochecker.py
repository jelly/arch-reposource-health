#!/usr/bin/python3

import glob
import os
import subprocess
import multiprocessing as mp


def verifysource(pkgbuilds, output):
    print('Verifying {} pkgbuilds'.format(len(pkgbuilds)))
    for pkgbuild in pkgbuilds:
        process = subprocess.Popen(['makepkg', '--verifysource'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=pkgbuild)
        _, err = process.communicate()
        if process.returncode != 0:
            pkgbase = os.path.basename(pkgbuild.rstrip('/trunk'))
            print('{}: source download failed', pkgbase)
            print(err.decode('utf-8'))
            
        subprocess.run(['git', 'clean', '-f'], cwd=pkgbuild)


def chunks(l, n=4):
    """ Yield n successive chunks from l.
    """
    newn = int(len(l) / n)
    for i in range(0, n-1):
        yield l[i*newn:i*newn+newn]
    yield l[n*newn-newn:]


if __name__ == "__main__":
    pkgbuilds = glob.glob('packages/**/trunk')
    parts = chunks(pkgbuilds, 8)
    output = mp.Queue()

    processes = [mp.Process(target=verifysource, args=(part, output)) for part in parts]

    # Run processes
    for p in processes:
        p.start()

    # Exit the completed processes
    for p in processes:
        p.join()

    # Get process results from the output queue
    results = [output.get() for p in processes]
    print(results)
