import libtorrent as lt

def kb_converter(rate_kb):
    if rate_kb > 1000:
        unit = "MB/s"
        rate = rate_kb / 1000
    else:
        unit = "kB/s"
        rate = rate_kb
        
    return (rate, unit)

def main():
    with open("magnets.txt", "r") as magnet_file:
        magnet_list = magnet_file.readlines()

    print(f"Launching with {len(magnet_list)} Magnets in Queue")
    job_counter = 1

    for magnet in magnet_list:
        print(f"\nStarting Magnet #{job_counter}")
        magnet = magnet.strip()
        ses = lt.session()
        ses.listen_on(6881, 6891)
        params = {
            'save_path': 'Downloads',
            'storage_mode': lt.storage_mode_t(2),
        }

        handle = lt.add_magnet_uri(ses, magnet, params)
        ses.start_dht()

        while (not handle.has_metadata()):
            print('Downloading Metadata...', end = "\r")

        while (handle.status().state != lt.torrent_status.seeding):
            s = handle.status()
            
            state_str = ['queued', 'checking', 'downloading metadata', \
                    'downloading', 'finished', 'seeding', 'allocating']
            
            progress = round(s.progress * 100)
            (down_rate, down_unit) = kb_converter(s.download_rate / 1000)
            (up_rate, up_unit) = kb_converter(s.upload_rate / 1000)
            peers = s.num_peers
            status = state_str[s.state]
            
            print(
                f"{status.capitalize()}: {progress}% - 📥 {round(down_rate)} {down_unit} 📤 {round(up_rate)} {up_unit} Peers: {peers}  ",
                end = "\r"
                )
            
        print(f"\nMagnet #{job_counter} Completed!")
        job_counter = job_counter + 1
        
if __name__ == "__main__":
    main()
