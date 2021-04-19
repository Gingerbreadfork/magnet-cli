import libtorrent as lt
import argparse

# Display Additional Output
verbose = True

arg_parser = argparse.ArgumentParser(
    prog='magnet-cli',
    usage='%(prog)s -m magnet_link',
    description='Download Magnets from the Command Line'
    )

arg_parser.add_argument('-m', '--magnet', help='download a magnet link', default=None)
arg_parser.add_argument('-t', '--torrent', help='download from a torrent file', default=None)

args = arg_parser.parse_args()

state_str = [
    'queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating'
    ]


def kb_converter(rate_kb):
    if rate_kb > 1000:
        unit = "MB/s"
        rate = rate_kb / 1000
    else:
        unit = "kB/s"
        rate = rate_kb
        
    return (rate, unit)


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
    s = handle.status()
    print(f"Torrent Download - {s.name}")
    
    while (handle.status().state != lt.torrent_status.seeding):
        s = handle.status()
        
        progress = round(s.progress * 100)
        (down_rate, down_unit) = kb_converter(s.download_rate / 1000)
        (up_rate, up_unit) = kb_converter(s.upload_rate / 1000)
        peers = s.num_peers
        status = state_str[s.state]
            
        print(
            f"{status.capitalize()}: {progress}% - 📥 {round(down_rate)} {down_unit} 📤 {round(up_rate)} {up_unit} Peers: {peers}  ",
            end = "\r"
            )
        
        alert_handler(session)

    print(s.status().name, 'complete')


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
        magnet = magnet.strip()
        session = lt.session()
        session.listen_on(6881, 6891)
        params = {
            'save_path': 'Downloads',
            'storage_mode': lt.storage_mode_t(2),
        }

        handle = lt.add_magnet_uri(session, magnet, params)
        session.start_dht()

        while (not handle.has_metadata()):
            print('Downloading Metadata...', end = "\r")

        while (handle.status().state != lt.torrent_status.seeding):
            s = handle.status()
            
            progress = round(s.progress * 100)
            (down_rate, down_unit) = kb_converter(s.download_rate / 1000)
            (up_rate, up_unit) = kb_converter(s.upload_rate / 1000)
            peers = s.num_peers
            status = state_str[s.state]
            
            print(
                f"{status.capitalize()}: {progress}% - 📥 {round(down_rate)} {down_unit} 📤 {round(up_rate)} {up_unit} Peers: {peers}  ",
                end = "\r"
                )
            
            alert_handler(session)

        if multiple == True:    
            print(f"\nMagnet #{job_counter} Completed")
            job_counter = job_counter + 1
        else:
            print("Download Completed")


if __name__ == "__main__":
    main()
