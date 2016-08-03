from svggen.library import getComponent


def test_make_arm():
    f = getComponent("ReducedArm")
    return f

if __name__ == '__main__':
    from svggen.utils.utils import printSummary
    c = test_make_arm()
    printSummary(c)

