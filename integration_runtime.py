"""Lazy adapters for advanced widgets; no network or third-party imports at import time."""
import tkinter as tk

class ModernTabs(tk.Frame):
    def __init__(self,master,pages=None,**kw):
        super().__init__(master)
        import customtkinter as ctk
        self.view=ctk.CTkTabview(self,command=lambda:self.event_generate('<<TabChanged>>',when='tail'),**kw);self.view.pack(fill='both',expand=True);self.pages={}
        for title in (pages or ['Page 1','Page 2']):self.add_page(title)
    def add_page(self,title):
        frame=self.view.add(title);self.pages[title]=frame;return frame
    def get(self):return self.view.get()
    def set(self,title):self.view.set(title)

class SheetView(tk.Frame):
    def __init__(self,master,data=None,headers=None,editable=True,**kw):
        super().__init__(master)
        from tksheet import Sheet
        self.sheet=Sheet(self,data=data or [],headers=headers or [],**kw);self.sheet.pack(fill='both',expand=True)
        self.sheet.enable_bindings('all' if editable else ('single_select','row_select','column_select','arrowkeys','copy','right_click_popup_menu'))
        self.sheet.bind('<<SheetModified>>',lambda event:self.event_generate('<<SheetChanged>>',when='tail'),add='+')
        self.sheet.bind('<<SheetSelect>>',lambda event:self.event_generate('<<SheetSelected>>',when='tail'),add='+')
    def get_data(self):return self.sheet.get_sheet_data()
    def set_data(self,data):self.sheet.set_sheet_data(data)
    def set_cell(self,row,column,value):self.sheet.set_cell_data(row,column,value);self.sheet.refresh()
    def get_cell(self,row,column):return self.sheet.get_cell_data(row,column)

class MapView(tk.Frame):
    def __init__(self,master,latitude=40.8518,longitude=14.2681,zoom=10,**kw):
        super().__init__(master)
        from tkintermapview import TkinterMapView
        self.map=TkinterMapView(self,**kw);self.map.pack(fill='both',expand=True);self.selected_position=None;self.selected_marker=None
        self.set_position(latitude,longitude);self.set_zoom(zoom);self.map.add_left_click_map_command(self._click)
    def _click(self,position):self.selected_position=position;self.event_generate('<<MapClicked>>',when='tail')
    def set_position(self,latitude,longitude):return self.map.set_position(latitude,longitude)
    def set_zoom(self,zoom):return self.map.set_zoom(zoom)
    def set_address(self,address):return self.map.set_address(address)
    def add_marker(self,latitude,longitude,text=''):
        def selected(marker):self.selected_marker=marker;self.event_generate('<<MarkerSelected>>',when='tail')
        return self.map.set_marker(latitude,longitude,text=text,command=selected)
    def clear_markers(self):self.map.delete_all_marker()
