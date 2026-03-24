from typing import List


class ExecutionController:
    def build_pytest_args(self, suite: str = 'all', use_mcp: bool = False) -> List[str]:
        args: List[str] = []

        mapping = {
            'ui': ['test_suites/ui', 'test_suites/bdd/features/ui'],
            'api': ['test_suites/api', 'test_suites/bdd/features/api'],
            'ui-bdd': ['test_suites/bdd/features/ui'],
            'api-bdd': ['test_suites/bdd/features/api'],
        }

        if suite in mapping:
            args.extend(mapping[suite])
        elif suite in ('smoke', 'regression'):
            args.extend(['-m', suite])
        elif suite != 'all':
            raise ValueError(f'Unsupported suite: {suite}')

        if use_mcp:
            args.append('--use-mcp')

        return args
