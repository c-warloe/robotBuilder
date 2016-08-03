def setup():
    # XXX HACK
    # The work that the builders do are directly in the build file
    # importing the build file will automatically invoke the builders
    from svggen import builders

