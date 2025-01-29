
from PyQt5.QtCore import Qt, QAbstractTableModel, QSortFilterProxyModel, QVariant
from PyQt5.QtGui import QColor

class DbTableModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        super(DbTableModel, self).__init__(parent)
        self.data = data
        if len(data) > 0:
            self.headers = data[0]._fields
        else:
            self.headers = []

    def rowCount(self, index):
        return len(self.data)

    def columnCount(self, index):
        return len(self.data[0])

    def data(self, QModelIndex, role=None):
        row = QModelIndex.row()
        column = QModelIndex.column()
        if role == Qt.DisplayRole:
            text = str(self.data[row][column])
            return text

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.headers[section])
            if orientation == Qt.Vertical:
                return str(section+1)

class LogMessageTableModel(DbTableModel):
    def __init__(self, data, parent=None):
        super(LogMessageTableModel, self).__init__(data, parent)

    def data(self, QModelIndex, role=None):
        row = QModelIndex.row()
        column = QModelIndex.column()
        if role == Qt.DisplayRole:
            text = str(self.data[row][column])
            return text
        if role == Qt.BackgroundColorRole:
            if self.data[row].Type == "ERROR":
                return QVariant(QColor(255, 210, 210))
            elif self.data[row].Type == "WARNING":
                return QVariant(QColor(254, 219, 187))

class DiceResultTableModel(DbTableModel):
    def __init__(self, data, parent=None):
        super(DiceResultTableModel, self).__init__(data, parent)

    def data(self, QModelIndex, role=None):
        row = QModelIndex.row()
        column = QModelIndex.column()
        if role == Qt.DisplayRole:
            text = str(self.data[row][column])
            return text
        if role == Qt.BackgroundColorRole:
            if self.data[row].UserGenerated == 1:
                return QVariant(QColor(210, 255, 210))

class ResultStatisticsTableModel(DbTableModel):
    def __init__(self, data, parent=None):
        super(ResultStatisticsTableModel, self).__init__(data, parent)
        self.headers = ["Position", "Name", "# 2 h", "avg 2 h", "# 4 h", "avg 4 h", "# today", "avg today", "#", "avg"]

    def data(self, QModelIndex, role=None):
        row = QModelIndex.row()
        column = QModelIndex.column()
        if role == Qt.DisplayRole:
            if (column == 1):
                text = str(self.data[row][column])
            else:
                text = self.data[row][column]
            return text

class LogMessageSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, clientId):
        super().__init__()
        self.clientId = clientId
        self.chkErrorStatus = True
        self.chkWarningStatus = True
        self.chkInfoStatus = True

    def chkErrorChanged(self, status=True):
        self.chkErrorStatus = status
        self.invalidateFilter()

    def chkWarningChanged(self, status=True):
        self.chkWarningStatus = status
        self.invalidateFilter()

    def chkInfoChanged(self, status=True):
        self.chkInfoStatus = status
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        src = self.sourceModel()
        if src is None:
            return False
        val = src.data[source_row].Type
        if val == "ERROR":
            return self.chkErrorStatus
        if val == "WARNING":
            return self.chkWarningStatus
        if val == "INFO":
            return self.chkInfoStatus
        return True