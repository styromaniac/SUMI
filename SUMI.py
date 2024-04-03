#!/usr/bin/env python3

import subprocess
import platform
import requests
import shutil
import sys
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

# Configurable variables
domain = "git.suyu.dev"
repo_owner = "suyu"
repo = "suyu"

os_name = platform.system()
arch = platform.machine()

app_ext = '.AppImage' if os_name == 'Linux' else '.dmg' if os_name == 'Darwin' else '.7z'
app_fldr = os.path.join(os.path.expanduser('~'), 'Applications')

os.makedirs(app_fldr, exist_ok=True)

log_f = os.path.join(app_fldr, f'{repo.title()}-{os_name}_{arch}-revision.log')
bkup_log_f = os.path.join(app_fldr, f'{repo.title()}-{os_name}_{arch}-backup-revision.log')
app_pth = os.path.join(app_fldr, f'{repo.title()}-{os_name}_{arch}{app_ext}')
bkup_pth = os.path.join(app_fldr, f'{repo.title()}-{os_name}_{arch}-backup{app_ext}')
temp_log_f = os.path.join(app_fldr, f'{repo.title()}-{os_name}_{arch}-temp-revision.log')
temp_pth = os.path.join(app_fldr, f'{repo.title()}-{os_name}_{arch}-temp{app_ext}')

releases_url = f"https://{domain}/api/v1/repos/{repo_owner}/{repo}/releases?limit=100"

def on_tv_row_act(tv, pth, col):
    model = tv.get_model()
    it = model.get_iter(pth)
    sel_row_val = model.get_value(it, 0)
    print("Selected:", sel_row_val)

def fetch_releases(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        return []
    releases = resp.json()
    return [release['tag_name'].replace('v', '') for release in releases]

def search_rev(search_rev):
    available_tags = fetch_releases(releases_url)
    return search_rev if search_rev in available_tags else "not_found"

def disp_msg(msg, use_markup=False):
    dialog = Gtk.MessageDialog(
        transient_for=None,
        flags=0,
        message_type=Gtk.MessageType.INFO,
        buttons=Gtk.ButtonsType.OK,
        text=msg
    )
    dialog.set_default_size(1280, 80)
    if use_markup:
        dialog.format_secondary_markup(msg)
    dialog.run()
    dialog.destroy()

def silent_ping(host, count=1):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, str(count), host]
    try:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        pass

def start_loader():
    dlg = Gtk.MessageDialog(
        transient_for=None,
        flags=0,
        message_type=Gtk.MessageType.INFO,
        buttons=Gtk.ButtonsType.NONE,
        text="Searching for revisions..."
    )
    dlg.set_title("Searching")
    dlg.set_default_size(1280, 80)
    ctxt = GLib.MainContext.default()
    while GLib.MainContext.iteration(ctxt, False):
        pass
    return dlg

def get_dl_url(tag):
    return f"https://{domain}/{repo_owner}/{repo}/releases/download/v{tag}/{repo.title()}-{os_name}_{arch}{app_ext}"

def gk_event_hdlr(widget, event, tv, lststore, dlg):
    if tv is not None and lststore is not None:
        on_k_press_event(event, tv, lststore, dlg)

def on_k_press_event(event, tv, lststore, dlg):
    keyname = Gdk.keyval_name(event.keyval)
    if keyname == 'BackSpace':
        handle_cancel(dlg)
    elif keyname == 'Return':
        handle_ok(tv, dlg)
    elif keyname == 'Escape':
        sys.exit(0)

def handle_ok(tv, dlg):
    model, tree_it = tv.get_selection().get_selected()
    if tree_it is not None:
        sel_row_val = model[tree_it][0]
        print("OK Selected:", sel_row_val)
        dlg.response(Gtk.ResponseType.OK)

def handle_cancel(dlg):
    print("Cancel action triggered")
    dlg.response(Gtk.ResponseType.CANCEL)

def search_dlg_k_event_hdlr(widget, event, dlg, entry):
    keyname = Gdk.keyval_name(event.keyval)
    if keyname == 'Return':
        dlg.response(Gtk.ResponseType.OK)
    elif keyname == 'Escape':
        dlg.response(Gtk.ResponseType.CANCEL)
    elif keyname == 'BackSpace':
        if not entry.is_focus():
            dlg.response(Gtk.ResponseType.CANCEL)

def ping_site():
    try:
        subprocess.run(["ping", "-c", "1", domain], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def read_revision_number(log_path):
    try:
        with open(log_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"

def prompt_revert_to_backup():
    installed_rev = read_revision_number(log_f)
    backed_up_rev = read_revision_number(bkup_log_f)

    message_text = f"Installed revision: {installed_rev}\n" \
                   f"Backup revision: {backed_up_rev}\n\n" \
                   f"Would you like to revert to the backup installation of {repo}?"

    dialog = Gtk.MessageDialog(
        transient_for=None,
        flags=0,
        message_type=Gtk.MessageType.QUESTION,
        buttons=Gtk.ButtonsType.YES_NO,
        text=message_text
    )
    response = dialog.run()
    dialog.destroy()
    return response == Gtk.ResponseType.YES

def rotate_files(current_path, backup_path, temp_path, current_log, backup_log, temp_log):
    if os.path.exists(current_path) and os.path.exists(backup_path):
        shutil.move(current_path, temp_path)
        shutil.move(backup_path, current_path)
        shutil.move(temp_path, backup_path)

    if os.path.exists(current_log) and os.path.exists(backup_log):
        shutil.move(current_log, temp_log)
        shutil.move(backup_log, current_log)
        shutil.move(temp_log, backup_log)

def revert_to_backup():
    if os.path.exists(app_pth) and os.path.exists(bkup_pth):
        rotate_files(app_pth, bkup_pth, temp_pth, log_f, bkup_log_f, temp_log_f)
        disp_msg(f"Successfully reverted to the backup installation of {repo}.")
    else:
        disp_msg("Backup installation not found.")

def create_prog_dlg():
    dlg = Gtk.MessageDialog(
        transient_for=None,
        flags=0,
        message_type=Gtk.MessageType.INFO,
        buttons=Gtk.ButtonsType.NONE,
        text="Downloading..."
    )
    dlg.set_default_size(1280, 80)
    prog_bar = Gtk.ProgressBar(show_text=True)
    dlg.vbox.pack_start(prog_bar, True, True, 0)
    dlg.show_all()
    return dlg, prog_bar

def dl_with_prog(url, out_pth):
    try:
        resp = requests.get(url, stream=True)
        if resp.status_code != 200:
            silent_ping(domain)
            if resp.status_code == 404:
                disp_msg("Failed to download the file. The revision might not be found.")
            else:
                disp_msg("Failed to download the file. Check your internet connection or try again later.")
            exit(1)
        total_size = int(resp.headers.get('content-length', 0))
        chunk_size = 1024
        dl_size = 0
        dlg, prog_bar = create_prog_dlg()
        with open(out_pth, 'wb') as f:
            try:
                for data in resp.iter_content(chunk_size=chunk_size):
                    f.write(data)
                    dl_size += len(data)
                    progress = dl_size / total_size
                    GLib.idle_add(prog_bar.set_fraction, progress)
                    GLib.idle_add(prog_bar.set_text, f"{int(progress * 100)}%")
                    while Gtk.events_pending():
                        Gtk.main_iteration()
                    if not dlg.get_visible():
                        raise Exception("Download cancelled by user.")
            except Exception as e:
                dlg.destroy()
                disp_msg(str(e))
                return
        dlg.destroy()
        if os_name == 'Darwin':
            mount_point = '/Volumes/{repo}'
            subprocess.run(['hdiutil', 'attach', '-mountpoint', mount_point, out_pth], check=True)
            app_path = os.path.join(mount_point, f'{repo.title()}.app')
            shutil.copytree(app_path, app_pth)
            subprocess.run(['hdiutil', 'detach', mount_point], check=True)
            os.remove(out_pth)
        elif os_name == 'Windows':
            extract_dir = os.path.splitext(out_pth)[0]
            subprocess.run(['7z', 'x', out_pth, f'-o{extract_dir}'], check=True)
            os.remove(out_pth)
        else:
            os.chmod(out_pth, 0o755)
    except Exception as e:
        disp_msg(f"Error: {str(e)}")
        return

# Main loop
def main():
    if not ping_site():
        if prompt_revert_to_backup():
            revert_to_backup()
        else:
            print("Exiting application.")
        return

    search_done = False
    rev = None
    while True:
        if not search_done:
            search_dlg = Gtk.MessageDialog(
                transient_for=None,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text="Enter a revision number to search for (leave blank to browse):"
            )
            search_dlg.set_default_size(1280, 80)
            entry = Gtk.Entry()
            entry.show()
            search_dlg.vbox.pack_end(entry, True, True, 0)
            search_dlg.connect("key-press-event", search_dlg_k_event_hdlr, search_dlg, entry)
            response = search_dlg.run()
            req_rev = entry.get_text() if response == Gtk.ResponseType.OK else None
            search_dlg.destroy()
            if req_rev:
                found_rev = search_rev(req_rev)
                if found_rev != "not_found":
                    installed_tag = read_revision_number(log_f)
                    if found_rev == installed_tag:
                        disp_msg(f"Revision {found_rev} is already installed.")
                        dlg.destroy()
                        continue
                    rev = found_rev
                    break
                else:
                    disp_msg(f"Revision {req_rev} not found.")
                    continue
            search_done = True

        loader_dlg = start_loader()
        available_tags = fetch_releases(releases_url)
        loader_dlg.destroy()
        if not available_tags:
            disp_msg("Failed to find available releases. Check your internet connection.")
            continue

        available_tags.sort(key=lambda x: [int(i) for i in x.split('.')], reverse=True)
        installed_tag = read_revision_number(log_f)
        bkup_tag = read_revision_number(bkup_log_f)
        menu_opts = [tag + (" (installed)" if tag == installed_tag else "") + (" (backed up)" if tag == bkup_tag else "") for tag in available_tags]

        lststore = Gtk.ListStore(str)
        for option in menu_opts:
            lststore.append([option])
        tv = Gtk.TreeView(model=lststore)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Revisions", renderer, text=0)
        tv.append_column(column)
        tv.connect("row-activated", on_tv_row_act)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(tv)
        dlg = Gtk.Dialog(title=f"Select {repo} rev.", transient_for=None, flags=0)
        dlg.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dlg.vbox.pack_start(scrolled_window, True, True, 0)
        dlg.set_default_size(80, 800)
        dlg.show_all()
        dlg.connect("key-press-event", gk_event_hdlr, tv, lststore, dlg)
        response = dlg.run()
        if response == Gtk.ResponseType.OK:
            selected_row = tv.get_selection().get_selected()[1]
            if selected_row is not None:
                rev_selection = lststore[selected_row][0]
                rev = rev_selection.replace(" (installed)", "").replace(" (backed up)", "")
                if rev == installed_tag:
                    disp_msg(f"Revision {rev} is already installed.")
                    dlg.destroy()
                    continue
        else:
            dlg.destroy()
            return
        dlg.destroy()
        break

    if os.path.exists(app_pth):
        shutil.move(app_pth, temp_pth)
        if os.path.isfile(log_f):
            shutil.copy(log_f, temp_log_f)

    skip_dl = False
    if os.path.isfile(bkup_log_f):
        bkup_rev = read_revision_number(bkup_log_f)
        if rev == bkup_rev:
            if os.path.exists(bkup_pth):
                rotate_files(app_pth, bkup_pth, temp_pth, log_f, bkup_log_f, temp_log_f)
            shutil.move(bkup_log_f, log_f)
            skip_dl = True

    if skip_dl:
        disp_msg(f"Revision {rev} has been installed from backup.")
    else:
        dl_url = get_dl_url(rev)
        dl_with_prog(dl_url, app_pth)
        with open(log_f, 'w') as f:
            f.write(str(rev))

        # Show a success dialog
        disp_msg(f"Revision {rev} has been successfully installed.")

    if os.path.exists(temp_pth):
        if os.path.exists(bkup_pth):
            os.remove(bkup_pth)
        shutil.move(temp_pth, bkup_pth)

    if os.path.exists(temp_log_f):
        if os.path.exists(bkup_log_f):
            os.remove(bkup_log_f)
        shutil.move(temp_log_f, bkup_log_f)

if __name__ == "__main__":
    main()
