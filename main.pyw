import os
from PyQt5 import QtCore, QtGui, QtWidgets
import ui
import enums
import urllib.request
from urllib.request import urlretrieve
import urllib.parse
from urllib.parse import urlencode
import requests
import json
from platformdirs import *
import random
import shutil
import sys
import subprocess
#import pkg_resources

class MainWindow(QtWidgets.QMainWindow, ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        
        for button in self.findChildren(QtWidgets.QPushButton):
            button.clicked.connect(lambda checked, button=button: self.on_button_clicked(button))
            
        for lineEdit in self.searchPage.findChildren(QtWidgets.QLineEdit):
            lineEdit.textChanged.connect(lambda text, lineEdit=lineEdit: self.on_lineEdit_changed(text, lineEdit))
        
        for comboBox in self.searchPage.findChildren(QtWidgets.QComboBox):
            comboBox.currentIndexChanged.connect(lambda index, comboBox=comboBox: self.on_comboBox_changed(index, comboBox))
        
        for spinBox in self.searchPage.findChildren(QtWidgets.QSpinBox):
            spinBox.valueChanged.connect(lambda value, spinBox=spinBox: self.on_spinBox_changed(value, spinBox))
            
        for doubleSpinBox in self.searchPage.findChildren(QtWidgets.QDoubleSpinBox):
            doubleSpinBox.valueChanged.connect(lambda value, spinBox=doubleSpinBox: self.on_spinBox_changed(value, spinBox))
            
        for checkBox in self.resultsPage.findChildren(QtWidgets.QCheckBox):
            checkBox.stateChanged.connect(lambda state, checkBox=checkBox: self.on_checkBox_changed(state, checkBox))
        
        self.genreBox.addItem("Any")
        self.languageBox.addItem("Any")
        for beatmapGenre in enums.BeatmapGenre:
            self.genreBox.addItem(beatmapGenre.name.title().replace("_", " ").capitalize())
        for beatmapLanguage in enums.BeatmapLanguage:
            self.languageBox.addItem(beatmapLanguage.name.title().replace("_", " ").capitalize())
        
        if os.path.exists(user_data_dir("Niche Map Downloader", "Doruat") + "/config.json"):
            with open(user_data_dir("Niche Map Downloader", "Doruat") + "/config.json", "r") as f:
                config = json.load(f)
                self.clientIDInput.setText(config.get("client_id", ""))
                self.clientSecretInput.setText(config.get("client_secret", ""))
                self.osuFolderDir.setText(config.get("osu_folder", ""))
                self.tempDLDir.setText(config.get("beatmap_download_folder", ""))
                self.stackedWidget.setCurrentWidget(self.searchPage)
        else:
            self.stackedWidget.setCurrentWidget(self.settingsPage)
                

    def on_button_clicked(self, button):
        match button:
            
            case self.settingsButton:
                self.stackedWidget.setCurrentWidget(self.settingsPage)
                button.setChecked(True)
                self.resultsTabButton.setChecked(False)
                self.searchTabButton.setChecked(False)
            
            case self.searchTabButton:
                self.stackedWidget.setCurrentWidget(self.searchPage)
                button.setChecked(True)
                self.resultsTabButton.setChecked(False)
                self.settingsButton.setChecked(False)
                
            case self.resultsTabButton:
                self.stackedWidget.setCurrentWidget(self.resultsPage)
                button.setChecked(True)
                self.searchTabButton.setChecked(False)
                self.settingsButton.setChecked(False)
                
            case self.osuFolderSelect:
                folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select osu! Folder", "")
                if folder:
                    self.osuFolderDir.setText(folder)
                    
            case self.selectDLDir:
                folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Beatmap Download Folder", "")
                if folder:
                    self.tempDLDir.setText(folder)
            
            case self.saveButton:
                if not self.clientIDInput.text() or not self.clientSecretInput.text() or not self.osuFolderDir.text() or not self.tempDLDir.text():
                    QtWidgets.QMessageBox.warning(self, "Error", "Please fill in all fields before saving.")
                    return
                osu_dir = self.osuFolderDir.text()
                temp_dir = self.tempDLDir.text()
                client_id = self.clientIDInput.text()
                client_secret = self.clientSecretInput.text()
                config={"client_id": client_id,
                        "client_secret": client_secret,
                        "osu_folder": osu_dir,
                        "beatmap_download_folder": temp_dir}
                                
                os.makedirs(user_data_dir("Niche Map Downloader", "Doruat"), exist_ok=True)
                with open(user_data_dir("Niche Map Downloader", "Doruat") + "/config.json", "w") as f:
                    json.dump(config, f, indent=4)
                    
                QtWidgets.QMessageBox.information(self, "Saved", "Credentials saved successfully!")
            
            case self.whyButton:
                QtWidgets.QMessageBox.information(self, "Why do I enter these?", "The API requires a token to access. Since I am not going to share my own credentials with everyone, you need to provide them yourself.")
            
            case self.goClientURL:
                QtWidgets.QMessageBox.information(self, "Get Client Credentials", "You will be redirected to the osu! website to create your own client credentials. Click on \"New OAuth Application\", fill in the required fields, and use the generated Client ID and Client Secret here.")
                QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://osu.ppy.sh/home/account/edit#oauth"))
            
            case self.beatmapInfoButton:
                self.stackedWidget_2.setCurrentWidget(self.beatmapInfoPage)
            
            case self.songInfoButton:
                self.stackedWidget_2.setCurrentWidget(self.songInfoPage)
            
            case self.miscButton:
                self.stackedWidget_2.setCurrentWidget(self.miscInfoPage)
            
            case self.moreButton:
                self.stackedWidget_3.setCurrentWidget(self.extraMiscPage)
            
            case self.lessInfoButton:
                self.stackedWidget_3.setCurrentWidget(self.normalMiscPage)

            case self.resetButton:
                for comboBox in self.searchPage.findChildren(QtWidgets.QComboBox):
                    comboBox.setCurrentIndex(0)
                for lineEdit in self.searchPage.findChildren(QtWidgets.QLineEdit):
                    lineEdit.clear()
                self.limitBox.setValue(1000)
    
            case self.searchButton:
                client_id = self.clientIDInput.text()
                client_secret = self.clientSecretInput.text()
                if client_id == "" or client_secret == "":
                    QtWidgets.QMessageBox.warning(self, "Error",
                                                  "Please set your client credentials in the settings tab before searching.")
                    return
                self.resultsTable.setRowCount(0)
                self.resultsTabButton.click()
                self.stackedWidget.setCurrentWidget(self.resultsPage)
                self.progressBar.setFormat("Preparing...")
                self.progressBar.setValue(0)
                QtWidgets.QApplication.processEvents()
                url = "https://osu.ppy.sh"
                authurl = f"{url}/oauth/token"
                beatmapurl = f"{url}/api/v2/beatmapsets/search"
                with open(user_data_dir("Niche Map Downloader", "Doruat") + "/config.json", "r") as f:
                    config = json.load(f)
                    token=config.get("token", "") if config.get("token", "") else ""
                headers_beatmap = {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "Authorization": f"Bearer {token}"
                }
                headers_auth = {
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded"
                }
                body_auth = {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "grant_type": "client_credentials",
                    "scope": "public"
                }
                data_auth = urllib.parse.urlencode(body_auth).encode()
                req_auth = urllib.request.Request(authurl, data=data_auth, headers=headers_auth, method="POST")
            
                self.progressBar.setFormat("Authing...")
                try:
                    with urllib.request.urlopen(req_auth) as response:
                        resp_data = response.read()
                        resp_json = json.loads(resp_data)
                        access_token = resp_json["access_token"]
                        config["token"] = access_token
                        with open(user_data_dir("Niche Map Downloader", "Doruat") + "/config.json", "w") as f:
                            json.dump(config, f, indent=4)
                        headers_beatmap["Authorization"] = f"Bearer {access_token}"
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"Failed to authenticate:\n{e}"
                                                f"\n\nPlease check your client credentials in the settings tab.")
                        
                self.progressBar.setFormat("Searching...")
                QtWidgets.QApplication.processEvents()
                beatmaps = []
                try:
                    cursor_string = ""
                    already_downloaded_ids = []
                    for folder in os.listdir(os.path.join(self.osuFolderDir.text(), "Songs")):
                        if os.path.isdir(os.path.join(self.osuFolderDir.text(), "Songs", folder)):
                            try:
                                beatmap_id = int(folder.split(" ")[0])
                                already_downloaded_ids.append(beatmap_id)
                            except:
                                continue
                    while len(beatmaps)<=self.limitBox.value():
                        req_url = f"{beatmapurl}?{self.qText}"
                        req_search = urllib.request.Request(req_url, headers=headers_beatmap, method="GET")
                        
                        with urllib.request.urlopen(req_search) as response:
                            resp_data = response.read()
                            resp_json = json.loads(resp_data)
                            beatmaps += resp_json["beatmapsets"]
                            cursor_string = resp_json.get("cursor_string", "")
                            self.progressBar.setValue(int(len(beatmaps)/self.limitBox.value()*100))
                            QtWidgets.QApplication.processEvents()
                        if not cursor_string:
                            break
                    
                    indexes_to_remove = []
                    for i, beatmap in enumerate(beatmaps):
                        if beatmap["id"] in already_downloaded_ids:
                            indexes_to_remove.append(i)
                            continue
                        circles = beatmap.get("count_circles", 0)
                        sliders = beatmap.get("count_sliders", 0)
                        spinners = beatmap.get("count_spinners", 0)
                        hit_length = beatmap.get("hit_length", 0)

                        total_objects = circles + sliders + spinners

                        if hit_length > 0:
                            taps_per_minute = total_objects / hit_length * 60
                        else:
                            taps_per_minute = 0

                        if total_objects > 0:
                            circle_ratio = circles / total_objects * 100
                        else:
                            circle_ratio = 0
                        if self.sliderCircleRatioMin.value()>0 and circle_ratio<self.sliderCircleRatioMin.value():
                            indexes_to_remove.append(i)
                            continue
                        if self.sliderCircleRatioMax.value()>0 and circle_ratio>self.sliderCircleRatioMax.value():
                            indexes_to_remove.append(i)
                            continue
                        if self.tpmMin.value()>0 and taps_per_minute<self.tpmMin.value():
                            indexes_to_remove.append(i)
                            continue
                        if self.tpmMax.value()>0 and taps_per_minute>self.tpmMax.value():
                            indexes_to_remove.append(i)
                            continue
                    for i in reversed(indexes_to_remove):
                        beatmaps.pop(i)
                    
                    for i, beatmap in enumerate(beatmaps):
                        if i >= self.limitBox.value():
                            break
                        
                        self.resultsTable.insertRow(self.resultsTable.rowCount())
                        self.resultsTable.setItem(i, 0, QtWidgets.QTableWidgetItem(str(beatmap["title"])))
                        self.resultsTable.setItem(i, 1, QtWidgets.QTableWidgetItem(beatmap["artist"]))
                        self.resultsTable.setItem(i, 2, QtWidgets.QTableWidgetItem(beatmap["creator"]))
                        self.resultsTable.setItem(i, 3, QtWidgets.QTableWidgetItem(str(len(beatmap["beatmaps"]))))
                        self.resultsTable.setItem(i, 4, QtWidgets.QTableWidgetItem(str(beatmap["id"])))
                except Exception as e:  
                    QtWidgets.QMessageBox.critical(self, "Error", f"Failed to retrieve beatmaps:\n{e}"
                                                   f"\n\nPlease check your internet connection and try again."
                                                   f"\nIf the problem persists, please check your client credentials in the settings tab or contact to @Doruat")
                
                self.progressBar.setValue(100)
                self.progressBar.setFormat(f"Search Completed, {self.resultsTable.rowCount()} Beatmapsets Have Found")
                QtWidgets.QApplication.processEvents()
                
            case self.downloadButton:
                QtWidgets.QMessageBox.information(self,"Notice","Download Started. Please make sure that you have enough disk space.")
                downloaded_files = []
                if self.randomDownloadCheck.isChecked():
                    i = 1
                    will_download = self.resultsTable.findItems("", QtCore.Qt.MatchContains)
                    for item in will_download:
                        if item.background().color() == QtGui.QColor(200, 200, 200):
                            row = item.row()
                            id = self.resultsTable.item(row, 4)
                            title = self.resultsTable.item(row, 0)
                            url = f"https://api.nerinyan.moe/d/{id.text()}"
                            temp_dir = self.tempDLDir.text()
                            try:
                                self.progressBar.setFormat(f"Downloading beatmap {i}/{len(will_download)}")
                                self.progressBar.setValue(int(i/len(will_download)*100))
                                QtWidgets.QApplication.processEvents()
                                urlretrieve(url, f"{temp_dir}/{id.text()} {title.text()}.osz")
                                downloaded_files.append(f"{temp_dir}/{id.text()} {title.text()}.osz")
                            except Exception as e:
                                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to download beatmap ID {id.text()}:\n{e}"
                                                       f"\n\nPlease check your internet connection and try again."
                                                       f"\nIf the problem persists, please contact to @Doruat")
                        i += 1
                else:
                    i = 1
                    for row in range(self.resultsTable.rowCount()):
                        id = self.resultsTable.item(row, 4)
                        title = self.resultsTable.item(row, 0)
                        url = f"https://api.nerinyan.moe/d/{id.text()}"
                        temp_dir = self.tempDLDir.text()
                        try:
                            self.progressBar.setFormat(f"Downloading beatmap {i}/{self.resultsTable.rowCount()}")
                            self.progressBar.setValue(int(i/self.resultsTable.rowCount()*100))
                            QtWidgets.QApplication.processEvents()
                            urlretrieve(url, f"{temp_dir}/{id.text()} {title.text()}.osz")
                            downloaded_files.append(f"{id.text()} {title.text()}.osz")
                        except Exception as e:
                            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to download beatmap ID {id.text()}:\n{e}"
                                                    f"\n\nPlease check your internet connection and try again."
                                                    f"\nIf the problem persists, please contact to @Doruat")
                        i += 1
                self.progressBar.setFormat("Download Completed, Moving Files...")
                QtWidgets.QApplication.processEvents()
                osu_songs_dir = os.path.join(self.osuFolderDir.text(), "Songs")
                for file in downloaded_files:
                    try:
                        shutil.move(os.path.join(temp_dir, file), os.path.join(osu_songs_dir, file))
                        self.progressBar.setValue(int(downloaded_files.index(file)/len(downloaded_files)*100))
                        self.progressBar.setFormat(f"Moving Files... ({downloaded_files.index(file)+1}/{len(downloaded_files)})")
                        QtWidgets.QApplication.processEvents()
                    except Exception as e:
                        QtWidgets.QMessageBox.critical(self, "Error", f"Failed to move file {file} to osu! Songs folder:\n{e}"
                                                f"\n\nPlease check if the osu! folder is correct and try again."
                                                f"\nIf the problem persists, please contact to @Doruat")
                self.progressBar.setValue(100)
                self.progressBar.setFormat("All Done!")
            
            
    query = {}
    
    def updateQuery(self):
        self.query = {k: v for k, v in self.query.items() if v not in ("", 0)}
        params = {}
        q_parts = []

        if 'artist' in self.query:
            q_parts.append(f'artist="{self.query["artist"]}"')

        if 'title' in self.query:
            q_parts.append(f'title="{self.query["title"]}"')

        if 'mapper' in self.query:
            q_parts.append(f'creator="{self.query["mapper"]}"')

        if 'status' in self.query:
            params['s'] = self.query['status']

        if 'genre' in self.query:
            params['g'] = self.query['genre']

        if 'language' in self.query:
            params['l'] = self.query['language']
        
        params['m']='0'

        if 'min_bpm' in self.query:
            q_parts.append(f'bpm>={self.query['min_bpm']}')

        if 'max_bpm' in self.query:
            q_parts.append(f'bpm<={self.query['max_bpm']}')

        if 'tag' in self.query:
            q_parts.append(f'tag="{self.query["tag"]}"')

        if 'manual' in self.query:
            q_parts.append(self.query['manual'])
        
        if 'min_difficulty' in self.query:
            q_parts.append(f'star>={self.query['min_difficulty']}')

        if 'max_difficulty' in self.query:
            q_parts.append(f'star<={self.query['max_difficulty']}')

        if 'min_ar' in self.query:
            q_parts.append(f'ar>={self.query['min_ar']}')

        if 'max_ar' in self.query:
            q_parts.append(f'ar<={self.query['max_ar']}')

        if 'min_od' in self.query:
            q_parts.append(f'od>={self.query['min_od']}')

        if 'max_od' in self.query:
            q_parts.append(f'od<={self.query['max_od']}')

        if 'min_cs' in self.query:
            q_parts.append(f'cs>={self.query['min_cs']}')

        if 'max_cs' in self.query:
            q_parts.append(f'cs<={self.query['max_cs']}')

        if 'min_hp' in self.query:
            q_parts.append(f'hp>={self.query['min_hp']}')

        if 'max_hp' in self.query:
            q_parts.append(f'hp<={self.query['max_hp']}')

        

        if q_parts:
            params['q'] = " ".join(q_parts)
        self.qText=urlencode(params,safe="><")
        self.queryLine.setText("")
        parts = [f"{k}={v}" for k, v in params.items()]
        self.queryLine.setText(" ".join(parts))
        
    def on_lineEdit_changed(self, text, lineEdit):
        match lineEdit:
            case self.titleLine:
                self.query["title"] = text.replace(" ","+")
            case self.artistLine:
                self.query["artist"] = text.replace(" ","+")
            case self.mapperLine:
                self.query["mapper"] = text.replace(" ","+")
            case self.manualLine:
                self.query["manual"] = text.replace(" ","+")
            case self.queryLine:
                return
        self.updateQuery()
    
    def on_comboBox_changed(self, index, comboBox):
        match comboBox:
            case self.statusBox:
                self.query["status"] = comboBox.currentText().lower()
            case self.genreBox:
                self.query["genre"] = enums.BeatmapGenre[comboBox.currentText().lower().replace(" ", "_")].value
            case self.languageBox:
                self.query["language"] = enums.BeatmapLanguage[comboBox.currentText().lower().replace(" ", "_")].value
            case self.tagBox:
                if comboBox.currentText() == "None":
                    if "tag" in self.query:
                        del self.query["tag"]
                else:
                    self.query["tag"] = comboBox.currentText().replace(" ", "+")
        self.updateQuery()
    
    def on_spinBox_changed(self, value, spinBox):
        match spinBox:
            case self.bpmMin:
                self.query["min_bpm"] = round(value, 2)
            case self.bpmMax:
                self.query["max_bpm"] = round(value, 2)
            case self.lenghtMin:
                self.query["min_length"] = round(value, 2)
            case self.lenghtMax:
                self.query["max_length"] = round(value, 2)
            case self.sMin:
                self.query["min_difficulty"] = round(value, 2)
            case self.sMax:
                self.query["max_difficulty"] = round(value, 2)
            case self.arMin:
                self.query["min_ar"] = round(value, 2)
            case self.arMax:
                self.query["max_ar"] = round(value, 2)
            case self.csMin:
                self.query["min_cs"] = round(value, 2)
            case self.csMax:
                self.query["max_cs"] = round(value, 2)
            case self.odMin:
                self.query["min_od"] = round(value, 2)
            case self.odMax:
                self.query["max_od"] = round(value, 2)
            case self.hpMin:
                self.query["min_hp"] = round(value, 2)
            case self.hpMax:
                self.query["max_hp"] = round(value, 2)
        self.updateQuery()
            
    def on_checkBox_changed(self, state, checkBox):
        if state == QtCore.Qt.Unchecked:
            match checkBox:
                case self.randomDownloadCheck:
                    for item in self.resultsTable.findItems("", QtCore.Qt.MatchContains):
                        item.setBackground(QtGui.QColor(255, 255, 255))
        else:
            match checkBox:
                case self.randomDownloadCheck:
                    for item in self.resultsTable.findItems("", QtCore.Qt.MatchContains):
                        item.setBackground(QtGui.QColor(255, 255, 255))
                    if self.downloadAmount.value() > self.resultsTable.rowCount():
                        dlamount=self.resultsTable.rowCount()
                    else:
                        dlamount=self.downloadAmount.value()
                    if self.downloadAmount.value() == 0:
                        dlamount=self.resultsTable.rowCount()
                        
                    row_count = self.resultsTable.rowCount()
                    rows = random.sample(range(row_count), dlamount)
                    for row in rows:
                        for col in range(self.resultsTable.columnCount()):
                            item = self.resultsTable.item(row, col)
                            if item:
                                item.setBackground(QtGui.QColor(200, 200, 200))
                                QtWidgets.QApplication.processEvents()
            

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
