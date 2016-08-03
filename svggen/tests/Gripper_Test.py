from svggen.library import getComponent


def test_make_gripper(display=False):
    f = getComponent("Gripper")

    f.setParameter("fingerlength", 40)
    f.setParameter("fingerwidth", 5)
    f.setParameter("width", 14)
    f.setParameter("depth", 9)

    f.makeOutput("output/gripper", display=display)


if __name__ == '__main__':
    test_make_gripper(display=True)

