import libtorrent as lt
import argparse

arg_parser = argparse.ArgumentParser(
    prog='magnet-cli',
    usage='%(prog)s -m magnet_link',
    description='Download Magnets from the Command Line'
    )

arg_parser.add_argument('-m', '--magnet', help='download a magnet link', default=None)
arg_parser.add_argument('-t', '--torrent', help='download from a torrent file', default=None)
arg_parser.add_argument('-v', '--verbose', help='display additional output', action='store_true', default=None)
arg_parser.add_argument('-s', '--stream', help='sequential download', action='store_true', default=None)
arg_parser.add_argument('-e', '--extra', help='add extra trackers from trackers.txt', action='store_true', default=None)


args = arg_parser.parse_args()

verbose = False if args.verbose == None else True
streaming = False if args.stream == None else True
extra_trackers = False if args.extra == None else True

state_str = [
    'Queued', 'Checking', 'Downloading Metadata', 'Downloading', 'Finished', 'Seeding', 'Allocating'
    ]

def magnet_add_trackers(magnet):
    with open("trackers.txt", "r") as tracker_file:
        tracker_list = tracker_file.readlines()

    tracker_list_prefixed = []
    
    for tracker in tracker_list:
        if tracker != "\n":
            prefixed = "&tr=" + tracker.strip()
            tracker_list_prefixed.append(prefixed)

    extended_magnet = magnet + "".join(tracker_list_prefixed)
    
    return extended_magnet


def kb_converter(rate_kb):
    if rate_kb > 1000:
        unit = "MB/s"
        rate = rate_kb / 1000
    else:
        unit = "kB/s"
        rate = rate_kb
        
    return (rate, unit)


def show_progress(status):
        progress = round(status.progress * 100)
        (down_rate, down_unit) = kb_converter(status.download_rate / 1000)
        (up_rate, up_unit) = kb_converter(status.upload_rate / 1000)
        peers = status.num_peers
        try:
            mode = state_str[status.state]
        except IndexError:
            print("Failed to Start Download...")
            raise SystemExit

        print(
            f"{mode}: {progress}% - 📥 {round(down_rate)} {down_unit} 📤 {round(up_rate)} {up_unit} Peers: {peers}  ",
            end = "\r"
            )


def alert_handler(ses):
    if verbose == True:
        alerts = ses.pop_alerts()
        for alert in alerts:
            if alert.category() & lt.alert.category_t.error_notification:
                print(alert)


def torrent_downloader(torrent):
    session = lt.session()
    info = lt.torrent_info(torrent)
    session.listen_on(6881, 6891)
    params = {
        'save_path': 'Downloads',
        'storage_mode': lt.storage_mode_t(2),
        'ti': info
    }

    handle = session.add_torrent(params)
    handle.set_sequential_download(True) if streaming == True else False
    status = handle.status()
    print(f"Downloading Torrent - {status.name}")
    
    while (handle.status().state != lt.torrent_status.seeding):
        status = handle.status()
        show_progress(status)
        alert_handler(session)

    print(f"Download Complete - {status.name}")
    raise SystemExit


def magnet_downloader(magnet):
        magnet = magnet.strip()
        
        if extra_trackers == True:
            magnet = magnet_add_trackers(magnet)
        
        session = lt.session()
        session.listen_on(6881, 6891)
        params = {
            'save_path': 'Downloads',
            'storage_mode': lt.storage_mode_t(2),
        }

        handle = lt.add_magnet_uri(session, magnet, params)
        handle.set_sequential_download(True) if streaming == True else False
        session.start_dht()

        while (not handle.has_metadata()):
            print('Downloading Metadata...', end = "\r")
        
        while (handle.status().state != lt.torrent_status.seeding):
            status = handle.status()
            show_progress(status)
            alert_handler(session)


def main():
    if args.torrent !=None:
        torrent_downloader(args.torrent)
    
    if args.magnet != None:
        multiple = False
        magnet_list = []
        magnet_list.append(args.magnet)
    else:
        with open("magnets.txt", "r") as magnet_file:
            magnet_list = magnet_file.readlines()

        if len(magnet_list) > 1:
            print(f"Launching with {len(magnet_list)} Magnets in Queue")
            multiple = True
        else:
            multiple = False

    job_counter = 1

    for magnet in magnet_list:
        if multiple == True:
            print(f"\nStarting Magnet #{job_counter}")

        magnet_downloader(magnet)
        
        if multiple == True:    
            print(f"\nMagnet #{job_counter} Completed")
            job_counter = job_counter + 1
        else:
            print("Download Completed")


if __name__ == "__main__":
    main()
