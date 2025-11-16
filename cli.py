import argparse

def build_parser():
    parser = argparse.ArgumentParser(
        description="CLI match-event tool"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--strict",
        help="validate json output",
        action="store_true"
    )
    group.add_argument(
        "--lenient",
        help="skip JSON schema validation (default)",
        action="store_true"
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output story file (default: out/story.json)",
        default="out/story.json"
    )

    return parser

def get_args():
    parser = build_parser()
    return parser.parse_args()
