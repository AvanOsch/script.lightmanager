# Import modules
import os, time, xbmc, xbmcaddon, xbmcgui, pyxbmct, subprocess

# Constants
ACTION_PREV_MENU = 10
ACTION_BACKSPACE = 110
ACTION_NAV_BACK  = 92
ACTION_SELECT    = 7

# Set plugin variables
__addon__ = xbmcaddon.Addon()

# Utils
def log(message,loglevel=xbmc.LOGNOTICE):
    xbmc.log(("@@@ LightManager: " + message).encode('UTF-8','replace'),level=loglevel)

# Get settings
remote    = __addon__.getSetting('remote')
lightman  = __addon__.getSetting('lightman')
sudo      = __addon__.getSetting('sudo')
housecode = __addon__.getSetting('house')
lightadr  = __addon__.getSetting('lightadr')
lightport = __addon__.getSetting('lightport')
lightnum  = 0
names     = []
types     = []
kinds     = []
dimms     = []
if sudo != '':
    lightman = 'echo "' + sudo + '" | sudo -S ' + lightman
if remote != "0":
    import urllib2
    if remote == "2":
        log('Check!')
        lightadr = xbmc.getIPAddress()
        cmd = ' -d -s -h ' + housecode + ' -p ' + lightport
        log('Starting Server: ' + lightman + cmd + '\n')
        try:
            p = subprocess.Popen(lightman + cmd, stdout=subprocess.PIPE, shell=True)
        except OSError:
            msg = 'FAILED: ' + cmd
            log(msg + '\n', xbmc.LOGDEBUG)
        out, err = p.communicate()
        if len(out.splitlines()) > 0:
            outmsg = str(out.splitlines()[0])
            log('Returned: ' + outmsg + '\n', xbmc.LOGDEBUG)
    lightman = 'http://' + lightadr + ':' + lightport + '/cmd='

# Get Device Settings
while True:
    ln = str(lightnum + 1)
    name = __addon__.getSetting('name' + ln)
    if name == "":
        break
    names.append(name)
    types.append(__addon__.getSetting('type' + ln))
    kinds.append(__addon__.getSetting('kind' + ln))
    dimms.append(float(__addon__.getSetting('dimm' + ln)))
    lightnum += 1
    log('Added settings for: ' + name + '\n', xbmc.LOGDEBUG)

# Classes
class LightDialog(pyxbmct.AddonDialogWindow):
    def __init__(self):
        log('Engage Lightmanager Dialog\n', xbmc.LOGDEBUG)
        super(LightDialog,self).__init__(__addon__.getLocalizedString(32200))
        rows = int(round((lightnum + 1) / 2) + 1)
        height = (rows * 50) + 50
        self.setGeometry(800,height,rows,6)
        self.set_controls(rows)
        self.set_navigation()

    def set_controls(self, rows):
        self.cbutton = []
        self.onbutton = []
        self.offbutton = []
        self.slider = []
        rownum = 0
        colnum = 0
        for n in range(lightnum):
            log('Creating controls for device: ' + str(n) + '\n', xbmc.LOGDEBUG)
            self.cbutton.append(pyxbmct.Button(names[n]))
            if (n == rows -1):
                colnum = 3
                rownum = 0
            self.placeControl(self.cbutton[n], rownum, colnum)
            log('Device kind is: ' + kinds[n] + ' - Type is: ' + types[n] + '\n', xbmc.LOGDEBUG)
            self.onbutton.append(0)
            self.offbutton.append(0)
            self.slider.append(0)
            if types[n] != "SCENE":
# InterTechno Dimmers of type "DIP" don't seem to accept percentage strings (work as "TOGGLE")
# The following line would automatically make "IT Dimmers" On/Off devices. 
#               if kinds[n] == "0" and (types[n] != "IT" or __addon__.getSetting('lurn' + str(n +1)) != "DIP"):
                if kinds[n] == "0":
                    self.slider[n] = pyxbmct.Slider()
                    self.placeControl(self.slider[n], rownum, colnum + 1, rowspan=1, columnspan=2)
                    self.slider[n].setPercent(dimms[n])
                else:
                    onbuttext = __addon__.getLocalizedString(32201)
                    offbuttext = __addon__.getLocalizedString(32202)
                    if kinds[n] == "2":
                        onbuttext = __addon__.getLocalizedString(32204)
                        offbuttext = __addon__.getLocalizedString(32205)
                    self.onbutton[n] = pyxbmct.Button(onbuttext)
                    self.placeControl(self.onbutton[n], rownum, colnum + 1)
                    self.offbutton[n] = pyxbmct.Button(offbuttext)
                    self.placeControl(self.offbutton[n], rownum, colnum + 2)
            rownum += 1
        self.msg_label = pyxbmct.Label('')
        self.placeControl(self.msg_label, rows - 1, 0, rowspan=1, columnspan=6)

    def set_navigation(self):
        for n in range(lightnum):
            nd = n + 1
            nu = n - 1
            if nd == lightnum:
                nd = 0
            if n == 0:
                self.setFocus(self.cbutton[n])
                self.msg_label.setLabel(names[n] + ': ' + __addon__.getLocalizedString(32206))
                nu = lightnum - 1
            if nu < 0:
                nu = 0
            if self.onbutton[n] != 0:
                self.cbutton[n].controlRight(self.onbutton[n])
                self.onbutton[n].controlRight(self.offbutton[n])
                self.onbutton[n].controlLeft(self.cbutton[n])
                self.onbutton[n].controlDown(self.cbutton[nd])
                self.onbutton[n].controlUp(self.cbutton[nu])
                self.offbutton[n].controlRight(self.cbutton[nd])
                self.offbutton[n].controlLeft(self.onbutton[n])
                self.offbutton[n].controlDown(self.cbutton[nd])
                self.offbutton[n].controlUp(self.cbutton[nu])
            else:
                if self.slider[n] != 0:
                    self.cbutton[n].controlRight(self.slider[n])
                    self.slider[n].controlDown(self.cbutton[nd])
                    self.slider[n].controlUp(self.cbutton[nu])
                else:
                    self.cbutton[n].controlRight(self.cbutton[nd])
            self.cbutton[n].controlLeft(self.cbutton[nu])
            self.cbutton[n].controlDown(self.cbutton[nd])
            self.cbutton[n].controlUp(self.cbutton[nu])

    def message_update(self):
        # Update message label when focus changes
        focused = self.getFocus()
        for n in range(lightnum):
            try:
                if focused == self.slider[n]:
                    dimms[n] = self.slider[n].getPercent()
                    log('Received Sliding Action from: ' + names[n] + ' - at ' + str(dimms[n]) + '\n', xbmc.LOGDEBUG)
                    self.msg_label.setLabel(names[n] + ': ' + str(int(dimms[n])) + '%   ' + __addon__.getLocalizedString(32211))
                    __addon__.setSetting('dimm' + str(n + 1), str(dimms[n]))
                    break
                if focused == self.cbutton[n]:
                    self.msg_label.setLabel(names[n] + ': ' + __addon__.getLocalizedString(32206))
                    break
                if focused == self.onbutton[n]:
                    msg = __addon__.getLocalizedString(32207)
                    if kinds[n] == "2":
                        msg = __addon__.getLocalizedString(32209)
                    self.msg_label.setLabel(names[n] + ': ' + msg)
                    break
                if focused == self.offbutton[n]:
                    msg = __addon__.getLocalizedString(32208)
                    if kinds[n] == "2":
                        msg = __addon__.getLocalizedString(32210)
                    self.msg_label.setLabel(names[n] + ': ' + msg)
                    break
            except (RuntimeError, SystemError):
                pass

    def notify(self, msg):
        oldMsg = self.msg_label.getLabel()
        self.msg_label.setLabel(msg)
        return oldMsg

    def execute_cmd(self, n, act=''):
        ln = str(n + 1)
        cmd = ''
        if remote == "0":
            if types[n] == "FS20":
                cmd += ' -h ' + housecode
            cmd += ' -c "'
        cmd += types[n]
        if types[n] == "IT" or types[n] == "IKEA":
            cmd += '%20' + __addon__.getSetting('code' + ln)
        cmd += '%20' + __addon__.getSetting('addr' + ln)
        if types[n] == "IT":
            cmd += '%20' + __addon__.getSetting('lurn' + ln)
        cmd += '%20' + act
        if remote == "0":
            cmd += '"'
            log('Executing: ' + lightman + cmd + '\n', xbmc.LOGDEBUG)
            try:
                p = subprocess.Popen(lightman + cmd, stdout=subprocess.PIPE, shell=True)
            except OSError:
                msg = 'FAILED: ' + cmd
                log(msg + '\n', xbmc.LOGDEBUG)
                dialog = xbmcgui.Dialog()
                dialog.notification('LightManager', msg, xbmcgui.NOTIFICATION_ERROR, 5000)
            out, err = p.communicate()
        else:
            out = '';
            log('Sending: ' + lightman + cmd + '\n', xbmc.LOGDEBUG)
            if cmd.endswith('%'):
                cmd += '25'
            try:
                p = urllib2.urlopen(lightman + cmd)
                out = p.read()
                p.close()
            except urllib2.HTTPError, err:
                msg = 'FAILED: ' + cmd + ', ' + str(err.reason)
                log(msg + '\n', xbmc.LOGDEBUG)
                dialog = xbmcgui.Dialog()
                dialog.notification('LightManager', __addon__.getLocalizedString(32214), xbmcgui.NOTIFICATION_ERROR, 5000)
            except urllib2.URLError, err:
                msg = 'FAILED: ' + cmd + ', ' + str(err.reason)
                log(msg + '\n', xbmc.LOGDEBUG)
                dialog = xbmcgui.Dialog()
                dialog.notification('LightManager', __addon__.getLocalizedString(32215), xbmcgui.NOTIFICATION_ERROR, 5000)
        if len(out.splitlines()) > 0:
            if remote == "0":
                outmsg = str(out.splitlines()[0])
            else:
                outmsg = str(out.splitlines()[7])[:-6]
            log('Returned: ' + outmsg + '\n', xbmc.LOGDEBUG)
            if "USB" in outmsg:
                dialog = xbmcgui.Dialog()
                dialog.notification('LightManager', __addon__.getLocalizedString(32213), xbmcgui.NOTIFICATION_ERROR, 5000)
            return outmsg
        else:
            return ''

    def onControl(self, control):
        msg = __addon__.getLocalizedString(32212)
        msgOld = ''
        for n in range(lightnum):
            try:
                if control == self.slider[n]:
                    msgOld = self.notify(names[n] + ': ' + msg + str(int(dimms[n])) + '%')
                    self.notify(self.execute_cmd(n, str(int(dimms[n])) + '%'))
                if control == self.cbutton[n]:
                    msgOld = self.notify(names[n] + ': ' + msg + __addon__.getLocalizedString(32203))
                    self.notify(self.execute_cmd(n, 'TOGGLE'))
                if control == self.onbutton[n]:
                    if kinds[n] == "2":
                        msgOld = self.notify(names[n] + ': ' + msg + __addon__.getLocalizedString(32204))
                        self.notify(self.execute_cmd(n, 'UP'))
                    else:
                        msgOld = self.notify(names[n] + ': ' + msg + __addon__.getLocalizedString(32201))
                        self.notify(self.execute_cmd(n, 'ON'))
                if control == self.offbutton[n]:
                    if kinds[n] == "2":
                        msgOld = self.notify(names[n] + ': ' + msg + __addon__.getLocalizedString(32205))
                        self.notify(self.execute_cmd(n, 'DOWN'))
                    else:
                        msgOld = self.notify(names[n] + ': ' + msg + __addon__.getLocalizedString(32202))
                        self.notify(self.execute_cmd(n, 'OFF'))
                if msgOld != '':
                    time.sleep(2)
                    self.notify(msgOld)
                    break
            except (RuntimeError, SystemError):
                pass

    def onAction(self, action):
        log('Received Action: ' + str(action.getId()) + '\n', xbmc.LOGDEBUG)
        if action in (ACTION_PREV_MENU, ACTION_BACKSPACE, ACTION_NAV_BACK):
            self.close()
        if action in (pyxbmct.ACTION_MOVE_LEFT, pyxbmct.ACTION_MOVE_RIGHT, pyxbmct.ACTION_MOVE_UP, pyxbmct.ACTION_MOVE_DOWN, pyxbmct.ACTION_MOUSE_DRAG):
            self.message_update()
        if action in (pyxbmct.ACTION_MOUSE_LEFT_CLICK, ACTION_SELECT) and self.getFocus() in self.slider:
            log('Received Slider Click!')
            control = self.getFocus()
            for n in range(lightnum):
                try:
                    if control == self.slider[n]:
                        dimms[n] = self.slider[n].getPercent()
                        msgOld = self.notify(names[n] + ': ' + __addon__.getLocalizedString(32212) + str(int(dimms[n])) + '%')
                        self.notify(self.execute_cmd(n, str(int(dimms[n])) + '%'))
                        time.sleep(2)
                        self.notify(msgOld)
                        break
                except (RuntimeError, SystemError):
                    pass

if __name__ == '__main__':
    lightManager = LightDialog()
    lightManager.doModal()
    del lightManager
