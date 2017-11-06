# -*- coding:utf-8 -*- 
import bqplot as bp
import ipywidgets as widgets
import traitlets
from IPython.display import display
import math
from tornado.template import Template

#表格MVC之model
class TableModel(traitlets.HasTraits):
   
    _pos = traitlets.Integer(0)
    _refresh = traitlets.Bool()
    _pagesize = traitlets.Integer(1)
    _header = traitlets.List([])
    _data = traitlets.List([])
    
    def __init__(self, header=[],data=[],pagesize=10):
    
        if isinstance(header, list):
            self._header = header
        else:
            raise Exception('header must be a list')
        if isinstance(data, list):
            self._data = data
        else:
            raise Exception('data must be a list')
        if isinstance(pagesize, int) and (pagesize > 0):
            self._pagesize = pagesize
        else:
            raise Exception('pagesuze must be a integer and >0') 
        
        #self.initPara()
    
    @traitlets.observe('_pos','_header')
    def _refreshPos(self,change):
        self._refresh = not(self._refresh)
              
    @property
    def page(self):
        if self._pos >= self._pagetotal:
            self._pos = 0
        start = self._pos * self._pagesize
        end = start + self._pagesize
        end = end if end <= self._recordtotal else self._recordtotal
        return self._data[start:end]
        
    def back(self):
        if self.pos <= self._pagetotal:
            self.pos = self.pos + 1
        #return self.page
    
    def previous(self):
        if (self.pos - 1) > 0 :
            self.pos = self.pos - 1
        #return self.page
    
    def first(self):
        self.pos = 1
        #return self.page
    
    def last(self):
        self.pos = self._pagetotal
        #return self.page
    
    @traitlets.observe('_pagesize','_data')
    def initPara(self,change=None):
        
        self._recordtotal = len(self._data)
        self._pagetotal = int(math.ceil(float(self._recordtotal) / self._pagesize))
        #self._pos = 1
        self._refresh = not(self._refresh)
    
    @property
    def pageTotal(self):
        return self._pagetotal

    @property
    def pageSize(self):
        return self._pagesize
    
    @pageSize.setter
    def pageSize(self,val):
        if isinstance(val, int) and int(val)>0:
            self._pagesize = int(val)
        else:
            raise('pageSize must be a integer  > 0')
            
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self,data=None):
        if data and isinstance(data, list):
            self._data = data
        else:
            raise Exception('data must be a list')
   
    
    @property
    def recordTotal(self):
        return self._recordtotal
    
    @property
    def header(self):
        return self._header
    
    @header.setter
    def header(self,header=[]):
        if isinstance(header, list):
            self._header = header
        else:
            raise Exception('header must be a list')
        
    
    @property
    def pos(self):
        return self._pos + 1
    
    @pos.setter
    def pos(self,pos=1):
        if isinstance(pos, int) and (pos > 0) and (pos <= self._pagetotal):
            self._pos = pos-1       


#表格MVC之view
class TableChart(widgets.VBox):
  
    T_Table = Template( """<table class='rendered_html table'> 
                          <tr>
                              {% for field in header %} <th>{{field}}</th>{% end %}
                          </tr>  
                          {% for row in data %} 
                              <tr> 
                                  {% for field in row %} 
                                      <td> {{ field }} </td> 
                                  {% end %}
                              </tr> 
                          {% end %} 
                      </table>
                  """
                 ) 
    _refresh_v = traitlets.Bool()    

    def update(self,change=None):
        table_html = self.T_Table.generate(header=self.model.header,data=self.model.page)
        self.html.value = table_html
        self.status.value = u'当前第%d页，共%d页' %(self.model.pos,self.model.pageTotal)
    
    def first(self,a):
        self.model.first()


    def back(self,a):
        self.model.back()


    def previous(self,a):
        self.model.previous()


    def last(self,a):
        self.model.last()

        
    def actionBar(self):
        self.btn_first = widgets.Button(icon='fa-step-backward',tooltip=u'第一页')
        self.btn_previous = widgets.Button(icon='fa-chevron-left',tooltip=u'上一页')
        self.btn_back = widgets.Button(icon='fa-chevron-right',tooltip=u'下一页')
        self.btn_last = widgets.Button(icon='fa-step-forward',tooltip=u'最后页')
        self.status = widgets.HTML()
        self.action = widgets.HBox(layout=widgets.Layout(width="100%",display='flex-flow',flex_flow='row', justify_content='space-around'))  
        self.action.children = [self.status,self.btn_first,self.btn_previous,self.btn_back,self.btn_last]
        #MVC之controller
        self.btn_first.on_click(self.first,False)
        self.btn_previous.on_click(self.previous,False)
        self.btn_back.on_click(self.back,False)   
        self.btn_last.on_click(self.last,False)   
        
    def __init__(self,header,body,pagesize=10):        
        super(TableChart,self).__init__()        
        self.model = TableModel(header,body,pagesize)
        self.html = widgets.HTML() 
        self.actionBar()

        self.update()
        self.children = [self.html,self.action]
        #和model保持同步 Observer模型
        self.model.observe(self.update,'_refresh')
         
