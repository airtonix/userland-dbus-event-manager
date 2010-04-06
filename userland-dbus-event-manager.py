#        Project Name : 
# Program Description : 
#         Designed By : Zenobius Jiricek
#          Created On : 2010-04-06
#          Created By : Zenobius Jiricek
#      Version Number :
#      Known Problems : 
import gtk

from eventmanager.manager import userland_dbus_manager

if __name__ == "__main__":
    gtk.gdk.threads_init()
    app = userland_dbus_manager()
    try:
        gtk.main()
    except KeyboardInterrupt:
        app.exit()


