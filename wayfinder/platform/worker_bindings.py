"""Adapt existing worker-owned definitions and dataclasses; no prompts or agent loop replaced."""
import dataclasses
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import types
import sys
from typing import Any, Union, get_args, get_origin, get_type_hints
import yaml
from pydantic import ConfigDict, TypeAdapter, create_model
from wayfinder.workers import schemas
from wayfinder.workers.W01_intent_analyst.schemas import IntentOutput

ROOT=Path(__file__).resolve().parents[1]/'workers'
# Tool-requiring W08/W11 remain excluded from this tools-closed source variant.
SOURCE_ROLES=frozenset({'W01','W03','W06','W07','W09','W10','W12','W13','W14','W15','W16','W18','W19','W24'})
PLATFORM_BINDINGS={'W02':'context.retrieve','W04':'catalog.search','W05':'platform.read_workflow','W25':'connectors.git','W26':'activity.read','W34':'files.discover','W35':'workers.local_file','W38':'context.retrieve','W41':'memory.conflicts','W42':'memory.maintenance','W44':'workflow.recovery','W46':'action.audit','W47':'workflow.evaluate'}

@lru_cache(maxsize=64)
def strict_type(annotation):
    if dataclasses.is_dataclass(annotation):
        hints=get_type_hints(annotation,globalns={**vars(sys.modules[annotation.__module__]),"Any":Any})
        fields={}
        for f in dataclasses.fields(annotation):
            default=f.default if f.default is not dataclasses.MISSING else f.default_factory() if f.default_factory is not dataclasses.MISSING else ...
            fields[f.name]=(strict_type(hints[f.name]),default)
        return create_model(annotation.__name__+'Transport',__config__=ConfigDict(extra='forbid',strict=True,allow_inf_nan=False),**fields)
    origin=get_origin(annotation);args=get_args(annotation)
    if origin is list:return list[strict_type(args[0])]
    if origin is dict:return dict[strict_type(args[0]),strict_type(args[1])]
    if origin in (Union,types.UnionType):return Union[tuple(strict_type(a) for a in args)]
    return annotation

@lru_cache(maxsize=1)
def definitions():
    result={}
    for path in sorted(ROOT.glob('*/definition.yaml')):
        raw=path.read_bytes();item=yaml.safe_load(raw)
        role=item['id']
        if role in result:raise ValueError('Duplicate worker definition.')
        output=item.get('output_contract')
        cls=IntentOutput if role=='W01' else getattr(schemas,output,None) if isinstance(output,str) else None
        if cls:model=strict_type(cls)
        elif role=='W08':model=create_model('WebResearchTransport',__config__=ConfigDict(extra='forbid',strict=True,allow_inf_nan=False),sources=(list[strict_type(schemas.SourceReference)],...),raw_sources=(dict[str,str],...),queries_issued=(list[str],...),urls_extracted=(int,...))
        else:raise ValueError('Worker definition has no supported existing output contract.')
        result[role]=dict(definition=item,sha256=hashlib.sha256(raw).hexdigest(),model=model,original=cls)
    return result

def instructions(role):
    if role not in SOURCE_ROLES:raise ValueError('This role requires a separately qualified connector or execution handler.')
    row=definitions()[role];item=row['definition']
    return ('Use this existing worker responsibility for the supplied context only. No tools, helpers, provider reads or effects are available. Missing evidence must remain missing. '
            +'Return only JSON matching the existing output schema. Responsibility: '+str(item['responsibility'])
            +' Acceptance criteria: '+json.dumps(item.get('acceptance_criteria',[]))
            +' Output schema: '+json.dumps(row['model'].model_json_schema()))

def restore(annotation,value):
    if dataclasses.is_dataclass(annotation):
        hints=get_type_hints(annotation,globalns={**vars(sys.modules[annotation.__module__]),"Any":Any})
        return annotation(**{k:restore(hints[k],v) for k,v in value.items()})
    origin=get_origin(annotation);args=get_args(annotation)
    if origin is list:return [restore(args[0],v) for v in value]
    if origin is dict:return {k:restore(args[1],v) for k,v in value.items()}
    return value

def semantic_errors(value):
    errors=value.validate() if dataclasses.is_dataclass(value) and hasattr(value,'validate') else []
    if dataclasses.is_dataclass(value):
        for f in dataclasses.fields(value):errors+=semantic_errors(getattr(value,f.name))
    elif isinstance(value,list):
        for v in value:errors+=semantic_errors(v)
    return errors

def validate_output(role,text):
    if role not in SOURCE_ROLES or not isinstance(text,str) or len(text.encode())>24000:raise ValueError('Invalid bounded worker output.')
    row=definitions()[role]
    checked=row['model'].model_validate_json(text)
    raw=checked.model_dump(mode='json')
    # Reuse the worker author's semantic validators as well as transport types.
    original=restore(row['original'],checked.model_dump())
    if semantic_errors(original):raise ValueError('Worker output failed its existing semantic contract.')
    if role=='W01' and (original.ambiguities or original.confidence<.6):original.requires_clarification=True
    serialized=json.dumps(dataclasses.asdict(original),allow_nan=False)
    if len(serialized.encode())>20000:raise ValueError('Structured output exceeds its platform evidence budget.')
    return json.loads(serialized)

def activation_ledger(compatible=False):
    found=definitions();rows=[]
    for i in range(1,48):
        role=f'W{i:02}';item=found.get(role)
        mode='supplied_context' if role in SOURCE_ROLES else 'trusted_service' if role in PLATFORM_BINDINGS else 'unqualified'
        rows.append(dict(id=role,definition_sha256=item['sha256'] if item else None,definition_present=bool(item),contract_validated=bool(item),binding=PLATFORM_BINDINGS.get(role) or ('hermes.definition/1' if role in SOURCE_ROLES else None),mode=mode,
            available=role in SOURCE_ROLES and compatible,live_qualified=False,
            required_permissions=['authenticated_owner_space_task','explicit_source_disclosure'] if role in SOURCE_ROLES else ['handler_specific_scope'],
            reason='Existing definition, strict output contract, tools-closed supplied-context variant; live role qualification is separate.' if role in SOURCE_ROLES else 'Existing trusted service; permission and availability enforced by its final handler.' if role in PLATFORM_BINDINGS else 'No qualified execution binding. Native, scheduling, provider effects and deferred fitness require their own qualification.'))
    return rows
