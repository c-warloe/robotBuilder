from svggen.library import getComponent

def test_make():
    component = getComponent("ReducedSeg")
    return component


if __name__ == '__main__':
    from svggen.utils.utils import printSummary
    c = test_make()
    printSummary(c)
