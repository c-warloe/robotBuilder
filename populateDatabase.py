from svggen.library import buildDatabase, filterComponents, getComponent, queryDatabase

def populateDatabase():
    buildDatabase(filterComponents())


if __name__ == '__main__':
    populateDatabase()
