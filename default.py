# Import modules
import os, time, xbmc, xbmcaddon, xbmcgui, pyxbmct, subprocess
# from threading import Timer

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
lightman  = __addon__.getSetting('lightman')
sudo      = __addon__.getSetting('sudo')
housecode = __addon__.getSetting('house')
lightnum  = 0
names     = []
types     = []
codes     = []
addrs     = []
kinds     = []
dimms     = []
if sudo != '':
    lightman = 'echo "' + sudo + '" | sudo -S ' + lightman
# Get Device Settings
while True:
    ln = str(lightnum + 1)
    name = __addon__.getSetting('name' + ln)
    if name == "":
        break
    names.append(name)
    types.append(__addon__.getSetting('type' + ln))
    codes.append(__addon__.getSetting('code' + ln))
    addrs.append(__addon__.getSetting('addr' + ln))
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
                self.msg_label.setLabel('{:}'.format(names[n] + ': ' + __addon__.getLocalizedString(32206)))
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
                    self.msg_label.setLabel('{:}'.format(names[n] + ': ' + str(int(dimms[n])) + '%   ' + __addon__.getLocalizedString(32211)))
                    __addon__.setSetting('dimm' + str(n + 1), str(dimms[n]))
                    break
                if focused == self.cbutton[n]:
                    self.msg_label.setLabel('{:}'.format(names[n] + ': ' + __addon__.getLocalizedString(32206)))
                    break
                if focused == self.onbutton[n]:
                    msg = __addon__.getLocalizedString(32207)
                    if kinds[n] == "2":
                        msg = __addon__.getLocalizedString(32209)
                    self.msg_label.setLabel('{:}'.format(names[n] + ': ' + msg))
                    break
                if focused == self.offbutton[n]:
                    msg = __addon__.getLocalizedString(32208)
                    if kinds[n] == "2":
                        msg = __addon__.getLocalizedString(32210)
                    self.msg_label.setLabel('{:}'.format(names[n] + ': ' + msg))
                    break
            except (RuntimeError, SystemError):
                pass

    def notify(self, msg):
        oldMsg = self.msg_label.getLabel()
        self.msg_label.setLabel(msg)
        return oldMsg

    def execute_cmd(self, n, act=''):
        cmd = ''
        if types[n] == "FS20":
            cmd += ' -h ' + housecode
        cmd += ' -c "' + types[n]
        if types[n] == "IT":
            cmd += ' ' + codes[n]
        cmd += ' ' + addrs[n] + act + '"'
        log('Executing: ' + lightman + cmd + '\n', xbmc.LOGDEBUG)
        try:
            p = subprocess.Popen(lightman + cmd, stdout=subprocess.PIPE, shell=True)
        except OSError:
            msg = 'FAILED: ' + cmd
            log(msg + '\n', xbmc.LOGDEBUG)
            dialog = xbmcgui.Dialog()
            dialog.notification('LightManager', msg, xbmcgui.NOTIFICATION_ERROR, 5000)
        out, err = p.communicate()
        if len(out.splitlines()) > 0:
            outmsg = str(out.splitlines()[0])
            log('Returned: ' + outmsg + '\n', xbmc.LOGDEBUG)
            if "USB" in outmsg:
                dialog = xbmcgui.Dialog()
                dialog.notification('LightManager', __addon__.getLocalizedString(32213), xbmcgui.NOTIFICATION_ERROR, 5000)
            return str(out.splitlines()[0])
        else:
            return ''

    def onControl(self, control):
        msg = __addon__.getLocalizedString(32212)
        msgOld = ''
        for n in range(lightnum):
            try:
                if control == self.slider[n]:
                    msgOld = self.notify('{:}'.format(names[n] + ': ' + msg + str(int(dimms[n])) + '%'))
                    self.notify('{:}'.format(self.execute_cmd(n, ' ' + str(int(dimms[n])) + '%')))
                if control == self.cbutton[n]:
                    msgOld = self.notify('{:}'.format(names[n] + ': ' + msg + __addon__.getLocalizedString(32203)))
                    self.notify('{:}'.format(self.execute_cmd(n, ' TOGGLE')))
                if control == self.onbutton[n]:
                    if kinds[n] == "2":
                        msgOld = self.notify('{:}'.format(names[n] + ': ' + msg + __addon__.getLocalizedString(32204)))
                        self.notify('{:}'.format(self.execute_cmd(n, ' UP')))
                    else:
                        msgOld = self.notify('{:}'.format(names[n] + ': ' + msg + __addon__.getLocalizedString(32201)))
                        self.notify('{:}'.format(self.execute_cmd(n, ' ON')))
                if control == self.offbutton[n]:
                    if kinds[n] == "2":
                        msgOld = self.notify('{:}'.format(names[n] + ': ' + msg + __addon__.getLocalizedString(32205)))
                        self.notify('{:}'.format(self.execute_cmd(n, ' DOWN')))
                    else:
                        msgOld = self.notify('{:}'.format(names[n] + ': ' + msg + __addon__.getLocalizedString(32202)))
                        self.notify('{:}'.format(self.execute_cmd(n, ' OFF')))
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
                        msgOld = self.notify('{:}'.format(names[n] + ': ' + __addon__.getLocalizedString(32212) + str(int(dimms[n])) + '%'))
                        self.notify('{:}'.format(self.execute_cmd(n, ' ' + str(int(dimms[n])) + '%')))
                        time.sleep(2)
                        self.notify(msgOld)
                        break
                except (RuntimeError, SystemError):
                    pass

if __name__ == '__main__':
    lightManager = LightDialog()
    lightManager.doModal()
    del lightManager

