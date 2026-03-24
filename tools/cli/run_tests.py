import sys

import pytest

from core.engine.execution_controller import ExecutionController


def main() -> None:
    suite = sys.argv[1] if len(sys.argv) > 1 else 'all'
    use_mcp = '--use-mcp' in sys.argv
    controller = ExecutionController()
    args = controller.build_pytest_args(suite=suite, use_mcp=use_mcp)
    raise SystemExit(pytest.main(args))


if __name__ == '__main__':
    main()
