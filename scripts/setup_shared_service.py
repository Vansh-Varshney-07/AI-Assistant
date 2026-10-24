"""Generate private credentials and configure the headless three-tier memory API."""
import argparse
import hashlib
import json
from pathlib import Path
import secrets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, default=Path('data/shared_service'))
    parser.add_argument('--tokenizer', type=Path, required=True,
                        help='Existing tokenizer.json for the consuming model.')
    parser.add_argument('--tokenizer-id', required=True,
                        help='Versioned identity of the consuming model/tokenizer.')
    args = parser.parse_args()
    tokenizer = args.tokenizer.resolve()
    if not tokenizer.is_file():
        parser.error('The consumer tokenizer must already exist.')
    root = args.runtime.resolve()
    config_path, keys_path = root / 'service.json', root / 'credentials.json'
    if config_path.exists() or keys_path.exists():
        parser.error('Existing configuration preserved; choose a fresh runtime.')
    root.mkdir(parents=True, exist_ok=True)
    (root / '.gitignore').write_text('*\n!.gitignore\n', encoding='utf-8')
    principals, keys = [], []
    for actor, role in [('user', 'user'), ('planner', 'agent'), ('reviewer', 'agent')]:
        token = secrets.token_urlsafe(32)
        keys.append(dict(tenant='default', actor=actor, role=role, token=token))
        principals.append(dict(tenant='default', actor=actor, role=role,
                               token_hash=hashlib.sha256(token.encode()).hexdigest()))
    config = dict(
        runtime=str(root), namespace='memory_' + secrets.token_hex(6),
        principals=principals,
        context=dict(
            tokenizer_path=str(tokenizer), tokenizer_id=args.tokenizer_id,
            profiles=[
                dict(actor_id='planner', version='1',
                     instructions='Use current supported requirements and cite their evidence.'),
                dict(actor_id='reviewer', version='1',
                     instructions='Check work against current requirements and flag missing evidence.')
            ], use_gpu=False,
        ),
    )
    config_path.write_text(json.dumps(config, indent=2), encoding='utf-8')
    keys_path.write_text(json.dumps(keys, indent=2), encoding='utf-8')
    print(f'Configuration: {config_path}\nPrivate credentials: {keys_path}\nTokens were not printed.')


if __name__ == '__main__':
    main()
