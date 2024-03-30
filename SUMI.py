#!/usr/bin/env python3

import subprocess
import requests
import shutil
import time
import sys
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

def get_os_arch():
    import platform
    os_name = platform.system()
    if os_name == 'Linux':
        arch = platform.machine()
        if arch == 'x86_64':
            return 'Linux', 'x86_64'
        elif arch == 'aarch64' or arch == 'arm64':
            return 'Linux', 'Arm64'
        else:
            raise Exception(f"Unsupported CPU architecture: {arch}")
    elif os_name == 'Darwin':
        arch = platform.machine()
        if arch == 'arm64':
            return 'macOS', 'Arm64'
        else:
            raise Exception(f"Unsupported CPU architecture: {arch}")
    else:
        raise Exception(f"Unsupported operating system: {os_name}")

os_name, arch = get_os_arch()

if os_name == 'Linux':
    app_ext = '.AppImage'
    app_fldr = os.path.join(os.environ['HOME'], 'Applications')
elif os_name == 'macOS':
    app_ext = '.app'
    app_fldr = '/Applications'
else:
    raise Exception(f"Unsupported operating system: {os_name}")

log_f = os.path.join(app_fldr, f'suyu-revision{app_ext}.log')
bkup_log_f = os.path.join(app_fldr, f'suyu-backup-revision{app_ext}.log')
appimg_pth = os.path.join(app_fldr, f'Suyu{app_ext}')
bkup_pth = os.path.join(app_fldr, f'Suyu-backup{app_ext}')
temp_log_f = f'/tmp/suyu-temp-revision{app_ext}.log'
temp_pth = f'/tmp/Suyu-temp{app_ext}'

releases_url = "https://git.suyu.dev/api/v1/repos/suyu/suyu/releases?limit=100"

def ensure_dir_exists(dir_pth):
    if not os.path.exists(dir_pth):
        os.makedirs(dir_pth)

ensure_dir_exists(app_fldr)

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
    for tag in available_tags:
        if tag == search_rev:
            return tag
    return "not_found"

def disp_msg(msg, use_markup=False):
    dialog = Gtk.Dialog(flags=0)
    dialog.set_default_size(1280, 80)
    label = Gtk.Label()
    if use_markup:
        label.set_markup(msg)
    else:
        label.set_text(msg)
    label.set_line_wrap(True) # Wrap long messages
    label.show()
    dialog.vbox.pack_start(label, True, True, 0)

    button = Gtk.Button.new_with_label("OK")
    button.connect("clicked", lambda w: dialog.destroy())
    button.show()
    dialog.action_area.pack_start(button, True, True, 0)

    dialog.show_all()
    dialog.run()
    dialog.destroy()

def silent_ping(host, count=1):
    try:
        subprocess.run(["ping", "-c", str(count), host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        subprocess.run(["ping", "-n", str(count), host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
    os_name, arch = get_os_arch()
    if os_name == 'Linux':
        return f"https://git.suyu.dev/suyu/suyu/releases/download/v{tag}/Suyu-{os_name}_{arch}.AppImage"
    elif os_name == 'macOS':
        return f"https://git.suyu.dev/suyu/suyu/releases/download/v{tag}/Suyu-{os_name}_{arch}.dmg"

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

def ping_suyu():
   try:
       subprocess.run(["ping", "-c", "1", "git.suyu.dev"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
       return True
   except subprocess.CalledProcessError:
       return False

def read_revision_number(log_path):
   try:
       with open(log_path, 'r') as f:
           return f.read().strip()
   except FileNotFoundError:
       return "unknown"  # Return a placeholder if the log file doesn't exist

def prompt_revert_to_backup():
   # Read the currently installed and backed up revision numbers
   installed_rev = read_revision_number(log_f)
   backed_up_rev = read_revision_number(bkup_log_f)

   # Construct the message text with the revision information
   message_text = f"Installed revision: {installed_rev}\n" \
                  f"Backup revision: {backed_up_rev}\n\n" \
                  "Would you like to revert to the backup installation of Suyu?"

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

def revert_to_backup():
   if os.path.exists(appimg_pth) and os.path.exists(bkup_pth):
       shutil.move(appimg_pth, temp_pth)  # Move current AppImage to a temporary location
       shutil.move(bkup_pth, appimg_pth)  # Move backup AppImage to the current location
       shutil.move(temp_pth, bkup_pth)  # Move the temporary AppImage to the backup location

       if os.path.exists(log_f) and os.path.exists(bkup_log_f):
           shutil.move(log_f, temp_log_f)  # Move current log to a temporary location
           shutil.move(bkup_log_f, log_f)  # Move backup log to the current log's location
           shutil.move(temp_log_f, bkup_log_f)  # Move the temporary log to the backup log's location

       # Show a success dialog with specified size
       dialog = Gtk.MessageDialog(
           transient_for=None,
           flags=0,
           message_type=Gtk.MessageType.INFO,
           buttons=Gtk.ButtonsType.OK,
           text="Successfully reverted to the backup installation of Suyu."
       )
       dialog.set_default_size(1280, 80)  # Set the dialog size
       dialog.run()
       dialog.destroy()
   else:
       # Show an error dialog if the backup installation is not found, with specified size
       dialog = Gtk.MessageDialog(
           transient_for=None,
           flags=0,
           message_type=Gtk.MessageType.ERROR,
           buttons=Gtk.ButtonsType.OK,
           text="Backup installation not found."
       )
       dialog.set_default_size(1280, 80)  # Set the dialog size
       dialog.run()
       dialog.destroy()

def create_prog_dlg(title="Downloading", text="Starting download..."):
   dlg = Gtk.Dialog(title)
   dlg.set_default_size(1280, 80)
   prog_bar = Gtk.ProgressBar(show_text=True)
   dlg.vbox.pack_start(prog_bar, True, True, 0)
   dlg.show_all()
   return dlg, prog_bar

def dl_with_prog(url, out_pth):
    try:
        resp = requests.get(url, stream=True)
        if resp.status_code != 200:
            silent_ping("git.suyu.dev")
            if resp.status_code == 404:
                disp_msg("Failed to download the AppImage. The revision might not be found.")
            else:
                disp_msg("Failed to download the AppImage. Check your internet connection or try again later.")
            main()
            return
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
        os.chmod(out_pth, 0o755)
    except Exception as e:
        disp_msg(f"Error: {str(e)}")
        main()
        return

# Main loop
def main():
   if not ping_suyu():
       user_choice = prompt_revert_to_backup()
       if user_choice:
           revert_to_backup()  # This will now show a success dialog upon completion
           return  # Exit after reverting to backup
       else:
           # If the user chooses not to revert, exit the application
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
           if response == Gtk.ResponseType.OK:
               req_rev = entry.get_text()
           else:
               req_rev = None
           search_dlg.destroy()
           if req_rev:
               found_rev = search_rev(req_rev)
               if found_rev != "not_found":
                   try:
                       with open(log_f, 'r') as f:
                           installed_tag = f.read().strip()
                   except FileNotFoundError:
                       installed_tag = ""
                   if found_rev == installed_tag:
                       disp_msg(f"Revision {found_rev} is already installed.")
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
       installed_tag = bkup_tag = ""
       try:
           with open(log_f, 'r') as f:
               installed_tag = f.read().strip()
           with open(bkup_log_f, 'r') as f:
               bkup_tag = f.read().strip()
       except FileNotFoundError:
           pass
       menu_opts = []
       for tag in available_tags:
           menu_entry = tag
           if tag == installed_tag:
               menu_entry += " (installed)"
           if tag == bkup_tag:
               menu_entry += " (backed up)"
           menu_opts.append(menu_entry)

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
       dlg = Gtk.Dialog(title="Select Suyu Revision", transient_for=None, flags=0)
       dlg.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
       dlg.vbox.pack_start(scrolled_window, True, True, 0)
       dlg.set_default_size(80, 800)
       dlg.show_all()
       dlg.connect("key-press-event", gk_event_hdlr, tv, lststore, dlg)
       response = dlg.run()
       if response == Gtk.ResponseType.CANCEL:
           dlg.destroy()
           return
       elif response == Gtk.ResponseType.OK:
           selected_row = tv.get_selection().get_selected()[1]
           if selected_row is not None:
               rev_selection = lststore[selected_row][0]
               rev = rev_selection.replace(" (installed)", "").replace(" (backed up)", "")
               if rev == installed_tag:
                   dlg.destroy()
                   disp_msg(f"Revision {rev} is already installed.")
                   continue
               break
           else:
               dlg.destroy()
               continue

   if os.path.isfile(appimg_pth):
       shutil.copy(appimg_pth, temp_pth)
       if os.path.isfile(log_f):
           shutil.copy(log_f, temp_log_f)
   skip_dl = False
   if os.path.isfile(bkup_log_f):
       with open(bkup_log_f, 'r') as f:
           bkup_rev = f.read().strip()
       if rev == bkup_rev:
           if os.path.isfile(bkup_pth):
               shutil.move(bkup_pth, appimg_pth)
           shutil.move(bkup_log_f, log_f)
           skip_dl = True
   else:
       skip_dl = False

   if skip_dl:
       disp_msg(f"Revision {rev} has been installed from backup.")
   else:
       if not skip_dl:
           appimg_url = get_dl_url(rev)
           dl_with_prog(appimg_url, appimg_pth)
           with open(log_f, 'w') as f:
               f.write(str(rev))

   if os.path.isfile(temp_pth):
       shutil.move(temp_pth, bkup_pth)
       if os.path.isfile(temp_log_f):
           shutil.move(temp_log_f, bkup_log_f)

if __name__ == "__main__":
   main()
