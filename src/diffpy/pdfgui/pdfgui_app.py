import argparse

from diffpy.pdfgui.version import __version__  # noqa


def main():
    parser = argparse.ArgumentParser(
        prog="diffpy.pdfgui",
        description=(
            "Graphical user interface program for structure refinements "
            "to the atomic pair distribution function.\n\n"
            "For more information, visit: "
            "https://github.com/diffpy/diffpy.pdfgui/"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show the program's version number and exit",
    )

    args = parser.parse_args()

    if args.version:
        print(f"diffpy.pdfgui {__version__}")
    else:
        # Default behavior when no arguments are given
        parser.print_help()


if __name__ == "__main__":
    main()
