import sys,os
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QFormLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QDir, QModelIndex, QItemSelectionModel
from engine.mainwindow import UI
from engine.tipselection import PopupWindow as tipPopup
from engine.timeview import PopupWindow as timePopup
import pyqtgraph as pg
from engine.experiment import MVexperiment,MVcurve
from pathlib import Path
import protocols.screening


class engine(object):
    def __init__(self) -> None:
        #set up the ui and the signal/slot connection
        self.ui = UI()
        self.DISABLE = False
        self.selected = 0
        self.ui.openfile.clicked.connect(self.open_files)
        self.ui.openfolder.clicked.connect(self.open_folder)
        self.ui.toggle_button.clicked.connect(self.toggle_button_clicked)
        #the model contains the tree of curve objects and is used for the treeview
        self.model = MVexperiment()
        self.ui.filelist.setModel(self.model)
        self.resizeView()
        self.ui.filelist.expanded.connect(self.resizeView)
        self.model.itemChanged.connect(self.changeDetected) #check for clicks on the checkbox       
        self.ui.filelist.clicked.connect(self.modChanged)
        self.ui.segmentSlider.valueChanged.connect(self.refreshView) #change the active segment and refresh the view
        self.ui.tipselect.clicked.connect(self.setTip)
        self.ui.timeview.clicked.connect(self.timeView)
        self.ui.slider.valueChanged.connect(self.slideCurves)
        self.loadPlugins()
        self.ui.sel_screen.currentIndexChanged.connect(self.screenSelected) #populate the screening area on demand
        self.ui.save.clicked.connect(self.saveDataset)
        
## These two functions manage the switching buttons. Maybe change the default to HDF5 soon? ##
        
    def toggle_button_clicked(self):
        if self.ui.toggle_button.isChecked():
            self.ui.toggle_button.setText("NHF")
            self.model.setProxy('Nanosurf')
            self.ui.toggle_button.setStyleSheet('color: red;')
            self.ui.timeview.setEnabled(False)
            self.ui.tipselect.setEnabled(True)
            self.ui.openfile.setText("Open file")
            self.ui.openfolder.setVisible(False)
        else:
            self.ui.toggle_button.setText("Optics11")
            self.model.setProxy('Optics11')
            self.ui.toggle_button.setStyleSheet('color: green;')
            self.ui.timeview.setEnabled(True)
            self.ui.tipselect.setEnabled(False)
            self.ui.openfile.setText("Open files")
            self.ui.openfolder.setVisible(True)
    

## 
# These two functions are to open files
# Opening always attaches to the existing list
# opening fills self.model of objects from experiment.py
# setCurves has to be launched, to create and connect the line objects
# refresh updates the view

    def open_folder(self): #opens and browses a folder
        fname = QFileDialog.getExistingDirectory(self.ui, 'Select the root dir', self.ui.wdir.text() )
        if fname == '' or fname is None or fname[0] == '':
            return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.model.createTree(fname,self.ui.limitOpen.isChecked())
        self.ui.wdir.setText(str(fname))
        self.setCurves()
        self.resizeView()
        self.refreshView()
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
        
    def open_files(self): #opens a bunch of files
        filename = QFileDialog.getOpenFileNames(self.ui, 'Select the file', self.ui.wdir.text())
        if filename == '' or filename is None or filename[0] == '' or len(filename[0])==0:
            return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        for fname in filename[0]:
            self.model.createTree(fname,limit=self.ui.limitOpen.isChecked())
        fname = Path(fname)
        self.ui.wdir.setText(str(fname.parents[0]))
        self.setCurves()
        self.resizeView()
        self.refreshView()
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)        

## After opening, connect lines ##

    def setCurves(self): #adds a curve to the model for each file added to it
        #row = self.model.itemFromIndex(self.model.index(first,0))
        self.model.pileup()
        curSeg = self.ui.segmentSlider.value()
        nsegs = 0
        for item in self.model.haystack:
            nsegs = max(nsegs,len(item.curve.segments))
            if item.line is None:
                x,y = item.curve.segments[curSeg].getCurve()
                item.line= pg.PlotCurveItem(x,y,pen='g')
                item.line.setClickable(True)
                self.ui.graphleft.addItem(item.line)
                item.line.parentitem = item
                item.line.sigClicked.connect(self.lineclick)
        self.ui.segmentSlider.setMaximum(nsegs-1)
        self.ui.nfiles.setText(str( len(self.model.haystack) ))
        self.ui.slider.setMaximum(len(self.model.haystack)-1)

## refreshing the view is crucial when changing segments ##
## resizing is just to make the ui experience smoother ##

    def resizeView(self):
        self.ui.filelist.resizeColumnToContents(0)

    def refreshView(self,curSeg=None):
        if curSeg is not None:
            for obj in self.model.haystack:
                obj.line.setData(*obj.curve.segments[curSeg].getCurve())
            self.ui.rightcurve.setData([],[])
            self.slideCurves(self.selected) #emulate changing selected
            
## Saving the haystack to disk ##    

    def saveDataset(self):
        extension = "Indentation map Files (*.hdf5)"
        from openers.saveHDF5 import saveHDF5 as saver
            
        fname = QFileDialog.getSaveFileName(self.ui, 'Save the experiment', self.ui.wdir.text(), extension)
        if fname == '' or fname is None or fname[0] == '':
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        fname = Path(fname[0])
        self.ui.wdir.setText(str(fname.parents[0]))
        prepare = saver(fname)
        prepare.setSegment(self.ui.segmentSlider.value())
        for obj in self.model.haystack:
            if obj.isCurve and obj.checkState() == Qt.CheckState.Checked:
                prepare.addCurve(obj.curve)
        prepare.save()        
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)  

## managing changes in selected curve ##
## the master is the select curve, which aligns: 
# - selected curve on the left
# - right curve
# - slider
# - selected item in the list

    def selectCurve(self,obj,newid=None):
        self.DISABLE=True # disable other actions while updating
        if newid is None:
            for i in range(len(self.model.haystack)):
                if obj == self.model.haystack[i]:
                    newid = i
                    break
        self.ui.rightcurve.setData(*obj.line.getData())
        if self.selected is not None:
            rowold = self.model.haystack[self.selected]
            color = rowold.line.opts['pen'].color().name()
            rowold.line.setPen(color=color,width=1)
        color = obj.line.opts['pen'].color().name()
        obj.line.setPen(color=color,width=3)
        self.ui.rightcurve.setData(*obj.line.getData())
        index = self.model.indexFromItem(obj)
        self.ui.filelist.setCurrentIndex(index)
        self.selected=newid
        self.ui.slider.setValue(self.selected)
        self.DISABLE = False
        
    def slideCurves(self,value): #triggered by the slider
        if self.DISABLE is False:
            self.selectCurve(self.model.haystack[value],value) 

    def lineclick(self,line): #line-click selection
        obj = line.parentitem
        self.selectCurve(obj)
            
    def modChanged(self,new): #list click selection
        if self.DISABLE is False:
            obj = self.model.itemFromIndex(new)
            if isinstance(obj,MVcurve) and obj.line is not None:
                self.selectCurve(obj)

## loading and using screening plugins from the protocols folder ##

    def loadPlugins(self):
        data = protocols.screening.list()
        self._plugin_screen = list(data.keys())
        for l in data.values():
            self.ui.sel_screen.addItem(l)
            
    def screenSelected(self,fid):
        if fid == 0:
            return
        layout = self.ui.box_cp.layout()
        if layout is None:
            layout = QFormLayout()
        self._screen = protocols.screening.get(self._plugin_screen[fid-1])
        
        self._screen.createUI(layout)
        self._screen.connect(self.calc)
        self.ui.box_cp.setLayout(layout)
        self.calc()
        
    def calc(self,*args):
        for item in self.model.haystack:
            if self._screen.do(*item.line.getData()) is False:
                item.setCheckState(Qt.CheckState.Unchecked)

## popup to view curves as a function of time and select segmentation mode ##

    def timeView(self):
        popup = timePopup(self.ui)
        popup.prepare(self.model.haystack)
        if popup.exec() == QDialog.DialogCode.Accepted:
            self.ui.segmentSlider.setValue(0)
            self.refreshView()
            nsegs = 0
            for item in self.model.haystack:
                nsegs = max(nsegs,len(item.curve.segments))
            self.ui.segmentSlider.setMaximum(nsegs-1)

## popup to set the tip geometry ##
            
    def setTip(self):
        popup = tipPopup(self.ui)
        if popup.exec() == QDialog.DialogCode.Accepted:
            geometry,value = popup.on_ok_clicked()
            
            for obj in self.model.haystack:
                obj.curve.tip['geometry']=geometry
                par = 1
                if geometry=='sphere' or geometry=='cylinder':
                    obj.curve.tip['parameter']='Radius'
                    obj.curve.tip['unit']='m'
                    par = 1e-6
                else:
                    obj.curve.tip['parameter']='Angle'
                    obj.curve.tip['unit']='deg'
                obj.curve.tip['value']=value*par
                #massimo
                
                #obj.parent().child(obj.row(),2).setText(geometry)
                #obj.parent().child(obj.row(),3).setText(f"{obj.curve.tip['parameter']}: {str(value)} {obj.curve.tip['unit']}")            
    
    def getRow(self,rowindex):
        return self.model.itemFromIndex(self.model.index(rowindex,0))
    
    def changeDetected(self,item): #manages changes to the view ?               
        if isinstance(item,MVcurve) and item.line is not None:
            if item.checkState() == Qt.CheckState.Checked:
                color = 'green'
            else:
                color='red'
            item.line.setPen(color=color,width=1)
        #for i in range(4):
        #    print(item.parent().child(item.row(),i).text())
        

def main():
    app = QApplication(sys.argv)
    theprogram = engine()
    theprogram.ui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
