"""AnyLogic Model Builder - Generates valid .alp files for AnyLogic 8.9.8."""

import re
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

PROCLIB = 'com.anylogic.libraries.processmodeling'

_ITEM_NAMES = {
    'Source':       '1412336242928',
    'Sink':         '1412336242929',
    'Delay':        '1412336242930',
    'SelectOutput': '1412336242931',
    'Queue':        '1412336242932',
    'Enter':        '1412336242933',
    'Seize':        '1412336243147',
    'Release':      '1412336243154',
    'Service':      '1412336243141',
    'ResourcePool': '1412336243135',
}

# Converter UUIDs from AnyLogic 8.9.8 ground-truth file
_CONVERTER_UUIDS = [
    "9f7858c9-b2c8-4ead-9244-fd08833f642b", "404652e6-561a-404c-aab2-ab7415f40ef5",
    "6fd6cd57-6dfe-4fc6-be0b-c74065351957", "3325dc48-3ad4-41e3-836f-dfd0e98fe1ed",
    "bb27038a-0f3a-48bb-b235-4a44066a14aa", "3f69ef3d-706e-41a6-8af0-11658c5eef68",
    "3f6fe405-e047-4304-91d6-6eee206d1106", "820d2b51-5b4a-48e7-b0b6-e46418e3c0f2",
    "630818fa-8975-4b70-976f-03180dce01db", "7c7e471c-004e-495e-a4ad-d840620ab38e",
    "3e38ff63-1f70-4ec0-b42c-e879b146785d", "b1eb86e4-14b3-405c-8257-56b80f1b485d",
    "d55f9fb6-86bb-45ea-9db1-79cecfa0ce91", "ab77aafd-8f02-4354-b789-928d45b1f73c",
    "e4f14fd7-1c4a-42e9-b91d-db2415f475db", "6d208120-6c7a-45a6-b411-402f18890d9b",
    "1816cdd0-177c-4973-9e88-dd8b95318556", "5c23f62f-06dc-46ad-8ead-688ec434e3e5",
    "5c7d7990-3f35-41eb-ae16-d0c16098acc6", "02a16c52-a834-4f30-b6af-a6aee51a294e",
    "f0988929-2718-4984-a1b6-c1f2ce152f1f", "1c9d9cfe-ea2b-43f9-8f62-dc31d8ed3ae1",
    "34cb742a-8ba4-47a7-87e6-f2685fe69e97", "4fe10751-c399-4752-94b7-30113ad45070",
    "c13fe5ac-6466-446e-886a-12df1431b1eb", "714f9ca2-426e-4bff-8569-2d18f58fdcf8",
    "045aeb5f-1087-4ac7-9702-a49404e7f7e8", "840e9a0a-de98-4b7d-a172-f9bbda2d6b98",
    "e342358b-75ed-4812-9376-6043fb6cb473", "f3d5ccdc-1bb3-466f-871d-f6b92a26cbb4",
    "59acb6fb-561c-4038-b722-a596a748b3c7", "be7e6726-05c0-4228-821d-a8df91aeb5bc",
    "df4a6a60-9ce8-4c6c-91c0-ad5a5d732259", "47491eb9-4606-42bd-8399-125a2b95fded",
    "9b2d1306-5d19-439a-8f2c-b144dd7e22fa", "ef421152-8732-4f97-9acb-c8e9a6890d5e",
    "d48f8080-25b1-44f5-8322-7bf2712ff974", "6c4de826-daad-4cd4-b703-51dfe803e822",
    "01af22d6-6889-4e98-a3df-e6eddc40fc92", "ea3b3dbe-cca2-4bde-957b-feaef7e18789",
    "e737c8c6-b526-4f88-b89e-554e205b0614", "efd24e87-d7f7-425f-9cb0-3ee17c7b2116",
    "a62607e6-047e-4910-a1ec-5426bf9283b5", "64dceb5b-de05-47c7-8e40-e9b293e80d75",
    "8d51c652-6aee-4de8-ba03-47b289a13ec5", "51d7b5ce-5664-4750-b1a0-fabcdc31e49a",
    "6522e3af-aa9e-421c-b667-e11db73cd8ca", "9ac073a0-7abf-4dff-826f-9c44d4780590",
    "2da9c21c-adc7-405a-a36e-46fbd9dfcd42", "fe4d1053-9c84-4221-bac7-cb489a7064ff",
    "1f005f88-e6d7-4bdc-81fa-3acf4c89cf64", "42dc5a7c-d7b1-4653-92b9-9359b46cc2d4",
    "e25721a9-34f9-479c-a4c3-31f5ec9e117d", "506d1de3-06df-4131-9e88-e43f1768e3d8",
    "e6625695-25a2-43d0-9056-1e9a1a594b1e", "91990287-4edf-4e38-aa6c-66d0e906807b",
    "2216cdd0-177c-5678-9e88-dd8b95312234", "1737c8c6-b526-4dd8-589e-ee4e205b06f4",
    "6a43bef6-8b70-4253-a828-82c3ab399655", "0a27038a-0f3a-48bb-b235-4a44066a1402",
    "0a9ec2c3-5e18-4c0a-a183-fd86d9d9a08b", "2216cdd0-177c-5678-9e88-dd8b95313334",
]


@dataclass
class ModelDefinition:
    name: str
    description: str
    time_unit: str = 'minutes'
    duration: float = 480
    agent_types: Optional[List[Dict]] = None
    uses_process_library: bool = True

    def __post_init__(self):
        if self.agent_types is None:
            self.agent_types = []


class _IDs:
    def __init__(self):
        self._n = int(time.time() * 1000)

    def next(self) -> int:
        self._n += 1
        return self._n


def _java_pkg(name: str) -> str:
    pkg = re.sub(r'[^a-zA-Z0-9]', '_', name).lower().strip('_')
    if pkg and pkg[0].isdigit():
        pkg = 'model_' + pkg
    return pkg or 'model'


_AGENT_PROPS = """\
			<AgentProperties>
				<EnvironmentDefinesInitialLocation>true</EnvironmentDefinesInitialLocation>
				<RotateAnimationTowardsMovement>true</RotateAnimationTowardsMovement>
				<RotateAnimationVertically>false</RotateAnimationVertically>
				<VelocityCode Class="CodeUnitValue">
					<Code><![CDATA[10]]></Code>
					<Unit Class="SpeedUnits"><![CDATA[MPS]]></Unit>
				</VelocityCode>
				<PhysicalLength Class="CodeUnitValue">
					<Code><![CDATA[1]]></Code>
					<Unit Class="LengthUnits"><![CDATA[METER]]></Unit>
				</PhysicalLength>
				<PhysicalWidth Class="CodeUnitValue">
					<Code><![CDATA[1]]></Code>
					<Unit Class="LengthUnits"><![CDATA[METER]]></Unit>
				</PhysicalWidth>
				<PhysicalHeight Class="CodeUnitValue">
					<Code><![CDATA[1]]></Code>
					<Unit Class="LengthUnits"><![CDATA[METER]]></Unit>
				</PhysicalHeight>
			</AgentProperties>
"""

_ENV_PROPS = """\
			<EnvironmentProperties>
					<EnableSteps>false</EnableSteps>
					<StepDurationCode Class="CodeUnitValue">
						<Code><![CDATA[1.0]]></Code>
						<Unit Class="TimeUnits"><![CDATA[SECOND]]></Unit>
					</StepDurationCode>
					<SpaceType>CONTINUOUS</SpaceType>
					<WidthCode><![CDATA[500]]></WidthCode>
					<HeightCode><![CDATA[500]]></HeightCode>
					<ZHeightCode><![CDATA[0]]></ZHeightCode>
					<ColumnsCountCode><![CDATA[100]]></ColumnsCountCode>
					<RowsCountCode><![CDATA[100]]></RowsCountCode>
					<NeigborhoodType>MOORE</NeigborhoodType>
					<LayoutType>USER_DEF</LayoutType>
					<NetworkType>USER_DEF</NetworkType>
					<ConnectionsPerAgentCode><![CDATA[2]]></ConnectionsPerAgentCode>
					<ConnectionsRangeCode><![CDATA[50]]></ConnectionsRangeCode>
					<NeighborLinkFractionCode><![CDATA[0.95]]></NeighborLinkFractionCode>
					<MCode><![CDATA[10]]></MCode>
			</EnvironmentProperties>
"""


def _datasets_props(ds_id: int) -> str:
    return f"""\
			<DatasetsCreationProperties>
				<AutoCreate>true</AutoCreate>
					<Id>{ds_id}</Id>
					<OccurrenceAtTime>true</OccurrenceAtTime>
					<OccurrenceDate>1779350400000</OccurrenceDate>
					<OccurrenceTime Class="CodeUnitValue">
						<Code><![CDATA[0]]></Code>
						<Unit Class="TimeUnits"><![CDATA[MINUTE]]></Unit>
					</OccurrenceTime>
					<RecurrenceCode Class="CodeUnitValue">
						<Code><![CDATA[1]]></Code>
						<Unit Class="TimeUnits"><![CDATA[MINUTE]]></Unit>
					</RecurrenceCode>
			</DatasetsCreationProperties>
"""


def _scale_ruler(ruler_id: int) -> str:
    return f"""\
			<ScaleRuler>
				<Id>{ruler_id}</Id>
				<Name><![CDATA[scale]]></Name>
				<X>0</X><Y>-150</Y>
				<PublicFlag>false</PublicFlag>
				<PresentationFlag>false</PresentationFlag>
				<ShowLabel>false</ShowLabel>
				<DrawMode>SHAPE_DRAW_2D3D</DrawMode>
				<Length>100</Length>
				<Rotation>0</Rotation>
				<ScaleType>BASED_ON_LENGTH</ScaleType>
				<ModelLength>10</ModelLength>
				<LengthUnits>METER</LengthUnits>
				<Scale>10</Scale>
				<InheritedFromParentAgentType>true</InheritedFromParentAgentType>
			</ScaleRuler>
"""


def _generic_param(param_id: int) -> str:
    return f"""\
			<GenericParameter>
				<Id>{param_id}</Id>
				<Name><![CDATA[{param_id}]]></Name>
				<GenericParameterValue Class="CodeValue">
					<Code><![CDATA[T extends Agent]]></Code>
				</GenericParameterValue>
				<GenericParameterLabel><![CDATA[Generic parameter:]]></GenericParameterLabel>
			</GenericParameter>
"""


def _agent_links(link_id: int) -> str:
    return f"""\
			<AgentLinks>
				<AgentLink>
					<Id>{link_id}</Id>
					<Name><![CDATA[connections]]></Name>
					<X>50</X><Y>-50</Y>
					<Label><X>15</X><Y>0</Y></Label>
					<PublicFlag>false</PublicFlag>
					<PresentationFlag>true</PresentationFlag>
					<ShowLabel>true</ShowLabel>
					<HandleReceiveInConnections>false</HandleReceiveInConnections>
					<AgentLinkType>COLLECTION_OF_LINKS</AgentLinkType>
					<AgentLinkBidirectional>true</AgentLinkBidirectional>
					<MessageType><![CDATA[Object]]></MessageType>
					<LineStyle>SOLID</LineStyle>
					<LineWidth>1</LineWidth>
					<LineColor>-16777216</LineColor>
					<LineZOrder>UNDER_AGENTS</LineZOrder>
					<LineArrow>NONE</LineArrow>
					<LineArrowPosition>END</LineArrowPosition>
				</AgentLink>
			</AgentLinks>
"""


def _level_presentation(level_id: int, time_plot_xml: str = '') -> str:
    inner = f'\t\t\t\t<Presentation>\n{time_plot_xml}\t\t\t\t</Presentation>\n' if time_plot_xml else ''
    return f"""\
			<Presentation>
				<Level>
					<Id>{level_id}</Id>
					<Name><![CDATA[level]]></Name>
					<X>0</X><Y>0</Y>
					<Label><X>10</X><Y>0</Y></Label>
					<PublicFlag>true</PublicFlag>
					<PresentationFlag>true</PresentationFlag>
					<ShowLabel>false</ShowLabel>
					<DrawMode>SHAPE_DRAW_2D3D</DrawMode>
					<Z>0</Z>
					<LevelVisibility>DIM_NON_CURRENT</LevelVisibility>
{inner}				</Level>
			</Presentation>
"""


def _gps_ref_only(pkg: str, classname: str, item_name: str) -> str:
    return f"""\
				<GenericParameterSubstitute>
					<GenericParameterSubstituteReference>
						<PackageName><![CDATA[{pkg}]]></PackageName>
						<ClassName><![CDATA[{classname}]]></ClassName>
						<ItemName><![CDATA[{item_name}]]></ItemName>
					</GenericParameterSubstituteReference>
				</GenericParameterSubstitute>
"""


def _entity_embedded_object(entity_name: str, entity_gp_id: int,
                            pkg: str, eo_id: int, db_id: int) -> str:
    return f"""\
					<EntityEmbeddedObject>
						<Id>{eo_id}</Id>
						<ActiveObjectClass>
							<PackageName><![CDATA[{pkg}]]></PackageName>
							<ClassName><![CDATA[{entity_name}]]></ClassName>
						</ActiveObjectClass>
						<GenericParameterSubstitute>
							<GenericParameterSubstituteReference>
								<PackageName><![CDATA[{pkg}]]></PackageName>
								<ClassName><![CDATA[{entity_name}]]></ClassName>
								<ItemName><![CDATA[{entity_gp_id}]]></ItemName>
							</GenericParameterSubstituteReference>
						</GenericParameterSubstitute>
						<Parameters>
						</Parameters>
						<ReplicationFlag>true</ReplicationFlag>
						<Replication Class="CodeValue">
							<Code><![CDATA[100]]></Code>
						</Replication>
						<CollectionType>ARRAY_LIST_BASED</CollectionType>
						<InitialLocationType>XYZ</InitialLocationType>
						<ColumnCode Class="CodeValue">
							<Code><![CDATA[0]]></Code>
						</ColumnCode>
						<RowCode Class="CodeValue">
							<Code><![CDATA[0]]></Code>
						</RowCode>
						<LocationNameCode Class="CodeValue">
							<Code><![CDATA[""]]></Code>
						</LocationNameCode>
						<InitializationType>LOAD_FROM_DATABASE</InitializationType>
						<InitializationDatabaseTableQuery>
							<Id>{db_id}</Id>
							<TableReference>
							</TableReference>
						</InitializationDatabaseTableQuery>
						<InitializationDatabaseType>ONE_AGENT_PER_DATABASE_RECORD</InitializationDatabaseType>
						<QuantityColumn>
						</QuantityColumn>
					</EntityEmbeddedObject>
"""


def _source_params(entity_name: str, entity_gp_id: int, pkg: str,
                   interarrival: str, eo_id: int, db_id: int) -> str:
    eo_xml = _entity_embedded_object(entity_name, entity_gp_id, pkg, eo_id, db_id)
    return f"""\
				<Parameters>
					<Parameter>
						<Name><![CDATA[arrivalType]]></Name>
						<Value Class="CodeValue">
							<Code><![CDATA[self.INTERARRIVAL_TIME]]></Code>
						</Value>
					</Parameter>
					<Parameter>
						<Name><![CDATA[rate]]></Name>
					</Parameter>
					<Parameter>
						<Name><![CDATA[interarrivalTime]]></Name>
						<Value Class="CodeUnitValue">
							<Code><![CDATA[{interarrival}]]></Code>
							<Unit Class="TimeUnits"><![CDATA[MINUTE]]></Unit>
						</Value>
					</Parameter>
					<Parameter>
						<Name><![CDATA[newEntity]]></Name>
						<Value Class="EntityCodeValue">
							<IsAgentEntity>true</IsAgentEntity>
{eo_xml}					</Value>
					</Parameter>
				</Parameters>
"""


def _queue_params() -> str:
    return """\
				<Parameters>
					<Parameter>
						<Name><![CDATA[capacity]]></Name>
						<Value Class="CodeValue">
							<Code><![CDATA[100000]]></Code>
						</Value>
					</Parameter>
				</Parameters>
"""


def _delay_params(capacity: str, delay_time: str) -> str:
    return f"""\
				<Parameters>
					<Parameter>
						<Name><![CDATA[capacity]]></Name>
						<Value Class="CodeValue">
							<Code><![CDATA[{capacity}]]></Code>
						</Value>
					</Parameter>
					<Parameter>
						<Name><![CDATA[delayTime]]></Name>
						<Value Class="CodeUnitValue">
							<Code><![CDATA[{delay_time}]]></Code>
							<Unit Class="TimeUnits"><![CDATA[MINUTE]]></Unit>
						</Value>
					</Parameter>
				</Parameters>
"""


def _sink_params() -> str:
    return """\
				<Parameters>
					<Parameter>
						<Name><![CDATA[onEnter]]></Name>
					</Parameter>
					<Parameter>
						<Name><![CDATA[destroyEntity]]></Name>
					</Parameter>
				</Parameters>
"""


def _embedded_object(block_id: int, name: str, btype: str,
                     x: int, y: int, db_id: int, params_xml: str) -> str:
    item_name = _ITEM_NAMES.get(btype, '1412336242928')
    gps = _gps_ref_only(PROCLIB, btype, item_name)
    return f"""\
				<EmbeddedObject>
					<Id>{block_id}</Id>
					<Name><![CDATA[{name}]]></Name>
					<X>{x}</X><Y>{y}</Y>
					<Label><X>-5</X><Y>-20</Y></Label>
					<PublicFlag>false</PublicFlag>
					<PresentationFlag>true</PresentationFlag>
					<ShowLabel>true</ShowLabel>
					<ActiveObjectClass>
						<PackageName><![CDATA[{PROCLIB}]]></PackageName>
						<ClassName><![CDATA[{btype}]]></ClassName>
					</ActiveObjectClass>
{gps}{params_xml}				<ReplicationFlag>false</ReplicationFlag>
					<Replication Class="CodeValue">
						<Code><![CDATA[100]]></Code>
					</Replication>
					<CollectionType>ARRAY_LIST_BASED</CollectionType>
					<InitialLocationType>XYZ</InitialLocationType>
					<ColumnCode Class="CodeValue">
						<Code><![CDATA[0]]></Code>
					</ColumnCode>
					<RowCode Class="CodeValue">
						<Code><![CDATA[0]]></Code>
					</RowCode>
					<LocationNameCode Class="CodeValue">
						<Code><![CDATA[""]]></Code>
					</LocationNameCode>
					<InitializationType>SPECIFIED_NUMBER</InitializationType>
					<InitializationDatabaseTableQuery>
						<Id>{db_id}</Id>
						<TableReference>
						</TableReference>
					</InitializationDatabaseTableQuery>
					<InitializationDatabaseType>ONE_AGENT_PER_DATABASE_RECORD</InitializationDatabaseType>
					<QuantityColumn>
					</QuantityColumn>
				</EmbeddedObject>
"""


def _connector(conn_id: int, idx: int, pkg: str,
               src_block: str, src_class: str,
               dst_block: str, dst_class: str,
               x: int, y: int, dx: int) -> str:
    return f"""\
				<Connector>
					<Id>{conn_id}</Id>
					<Name><![CDATA[connector{idx if idx > 0 else ''}]]></Name>
					<X>{x}</X><Y>{y}</Y>
					<Label><X>10</X><Y>0</Y></Label>
					<PublicFlag>false</PublicFlag>
					<PresentationFlag>true</PresentationFlag>
					<ShowLabel>false</ShowLabel>
					<SourceEmbeddedObjectReference>
						<PackageName><![CDATA[{pkg}]]></PackageName>
						<ClassName><![CDATA[Main]]></ClassName>
						<ItemName><![CDATA[{src_block}]]></ItemName>
					</SourceEmbeddedObjectReference>
					<SourceConnectableItemReference>
						<PackageName><![CDATA[{PROCLIB}]]></PackageName>
						<ClassName><![CDATA[{src_class}]]></ClassName>
						<ItemName><![CDATA[out]]></ItemName>
					</SourceConnectableItemReference>
					<TargetEmbeddedObjectReference>
						<PackageName><![CDATA[{pkg}]]></PackageName>
						<ClassName><![CDATA[Main]]></ClassName>
						<ItemName><![CDATA[{dst_block}]]></ItemName>
					</TargetEmbeddedObjectReference>
					<TargetConnectableItemReference>
						<PackageName><![CDATA[{PROCLIB}]]></PackageName>
						<ClassName><![CDATA[{dst_class}]]></ClassName>
						<ItemName><![CDATA[in]]></ItemName>
					</TargetConnectableItemReference>
					<Points>
						<Point><X>0</X><Y>0</Y></Point>
						<Point><X>{dx}</X><Y>0</Y></Point>
					</Points>
				</Connector>
"""


_CHART_COLORS = [-10496, -6632142, -13434879, -16711936, -16776961]


def _collect_chart_series(agent_types: List[Dict]) -> List[Dict]:
    delay_count = sum(1 for at in agent_types for b in at.get('blocks', []) if b['type'] == 'Delay')
    series = []
    ci = 0
    for at in agent_types:
        for block in at.get('blocks', []):
            if block['type'] == 'Delay':
                queue_name = block['name'] + 'Queue'
                title = 'Queue Size' if delay_count == 1 else f'{block["name"]} Queue'
                series.append({'title': title, 'expression': f'{queue_name}.size()',
                                'color': _CHART_COLORS[ci % len(_CHART_COLORS)]})
                ci += 1
            elif block['type'] == 'Sink':
                series.append({'title': 'Throughput', 'expression': f'{block["name"]}.count()',
                                'color': _CHART_COLORS[ci % len(_CHART_COLORS)]})
                ci += 1
    return series


def _dataset_expression(idx: int, title: str, expression: str, color: int, ds_id: int) -> str:
    ds_name = f'dataset{idx}' if idx > 0 else 'dataset'
    return f"""\
					<DatasetExpression>
						<Title><![CDATA[{title}]]></Title>
						<Id>{ds_id}</Id>
						<Expression><![CDATA[{ds_name}]]></Expression>
						<Color>{color}</Color>
						<Expression2><![CDATA[{expression}]]></Expression2>
						<Expression2Flag>true</Expression2Flag>
						<PointStyle>NONE</PointStyle>
						<LineWidth>1.0</LineWidth>
					</DatasetExpression>
"""


def _time_plot(plot_id: int, rec_id: int, datasets_xml: str) -> str:
    return f"""\
				<TimePlot>
					<Id>{plot_id}</Id>
					<Name><![CDATA[plot]]></Name>
					<X>470</X><Y>170</Y>
					<Label><X>0</X><Y>-10</Y></Label>
					<PublicFlag>true</PublicFlag>
					<PresentationFlag>true</PresentationFlag>
					<ShowLabel>false</ShowLabel>
					<DrawMode>SHAPE_DRAW_2D3D</DrawMode>
					<AutoUpdate>true</AutoUpdate>
					<RecurrenceProperties>
						<Id>{rec_id}</Id>
						<OccurrenceAtTime>true</OccurrenceAtTime>
						<OccurrenceDate>1779350400000</OccurrenceDate>
						<OccurrenceTime Class="CodeUnitValue">
							<Code><![CDATA[0]]></Code>
							<Unit Class="TimeUnits"><![CDATA[MINUTE]]></Unit>
						</OccurrenceTime>
						<RecurrenceCode Class="CodeUnitValue">
							<Code><![CDATA[1]]></Code>
							<Unit Class="TimeUnits"><![CDATA[MINUTE]]></Unit>
						</RecurrenceCode>
					</RecurrenceProperties>
					<EmbeddedIcon>false</EmbeddedIcon>
					<Width>260</Width>
					<Height>210</Height>
					<BackgroundColor/>
					<BorderColor/>
					<ChartArea>
						<XOffset>50</XOffset><YOffset>30</YOffset>
						<Width>180</Width><Height>120</Height>
						<BackgroundColor>-1</BackgroundColor>
						<BorderColor>-16777216</BorderColor>
						<GridColor>-12566464</GridColor>
					</ChartArea>
					<Legend>
						<Place>SOUTH</Place>
						<TextColor>-16777216</TextColor>
						<Size>30</Size>
					</Legend>
					<Labels>
						<HorLabelsPosition>DEFAULT</HorLabelsPosition>
						<VerLabelsPosition>DEFAULT</VerLabelsPosition>
						<TextColor>-12566464</TextColor>
					</Labels>
					<ShowLegend>true</ShowLegend>
					<TimeWindowsMovementType>MOVEMENT_WITH_TIME</TimeWindowsMovementType>
					<TimeWindowUnits>MODEL_TIME_UNIT</TimeWindowUnits>
					<VerScaleFromExpression><![CDATA[0]]></VerScaleFromExpression>
					<VerScaleToExpression><![CDATA[1]]></VerScaleToExpression>
					<VerScaleType>AUTO</VerScaleType>
					<DrawLine>true</DrawLine>
					<Interpolation>LINEAR</Interpolation>
{datasets_xml}				<SamplesToKeep>100</SamplesToKeep>
					<TimeWindowExpression><![CDATA[100]]></TimeWindowExpression>
					<FillAreaUnderLine>false</FillAreaUnderLine>
					<LabelFormat>MODEL_TIME_UNITS</LabelFormat>
				</TimePlot>
"""


def _active_object_class(cls_id: int, name: str, gp_id: int, ds_id: int,
                         scale_id: int, link_id: int, level_id: int,
                         is_main: bool, embedded: str, connectors: str,
                         time_plot_xml: str = '') -> str:
    if is_main:
        flow_sections = f"""\
			<Connectors>
{connectors}		</Connectors>
{_agent_links(link_id)}
			<EmbeddedObjects>
{embedded}		</EmbeddedObjects>

"""
    else:
        flow_sections = f"""\
{_agent_links(link_id)}

"""
    return f"""\
		<ActiveObjectClass>
			<Id>{cls_id}</Id>
			<Name><![CDATA[{name}]]></Name>
			<Generic>false</Generic>
{_generic_param(gp_id)}		<FlowChartsUsage>ENTITY</FlowChartsUsage>
			<SamplesToKeep>100</SamplesToKeep>
			<LimitNumberOfArrayElements>false</LimitNumberOfArrayElements>
			<ElementsLimitValue>100</ElementsLimitValue>
			<MakeDefaultViewArea>true</MakeDefaultViewArea>
			<SceneGridColor/>
			<SceneBackgroundColor>-4144960</SceneBackgroundColor>
			<SceneSkybox>null</SceneSkybox>
{_AGENT_PROPS}{_ENV_PROPS}{_datasets_props(ds_id)}{_scale_ruler(scale_id)}		<CurrentLevel>{level_id}</CurrentLevel>
			<ConnectionsId>{link_id}</ConnectionsId>
{flow_sections}{_level_presentation(level_id, time_plot_xml if is_main else '')}	</ActiveObjectClass>
"""


def _build_flow(agent_types: List[Dict], pkg: str, ids: '_IDs',
                entity_gp_ids: Dict[str, int]) -> tuple:
    embedded = ''
    connectors = ''

    for at in agent_types:
        entity_name = at['name']
        entity_gp_id = entity_gp_ids[entity_name]
        blocks = at.get('blocks', [])
        built = []

        # Auto-inject Queue before each Delay to buffer when capacity is full
        expanded = []
        for block in blocks:
            if block['type'] == 'Delay':
                expanded.append({'type': 'Queue', 'name': block['name'] + 'Queue', 'params': {}})
            expanded.append(block)
        blocks = expanded

        x = 150
        for i, block in enumerate(blocks):
            bid = ids.next()
            btype = block['type']
            params = block.get('params', {})
            db_id = ids.next()

            if btype == 'Source':
                eo_id = ids.next()
                eo_db_id = ids.next()
                params_xml = _source_params(
                    entity_name, entity_gp_id, pkg,
                    params.get('interarrivalTime', 'exponential(10)'),
                    eo_id, eo_db_id,
                )
            elif btype == 'Queue':
                params_xml = _queue_params()
            elif btype == 'Delay':
                params_xml = _delay_params(
                    params.get('capacity', '1'),
                    params.get('delayTime', 'triangular(5,10,15)')
                )
            else:
                params_xml = _sink_params()

            embedded += _embedded_object(bid, block['name'], btype, x, 80, db_id, params_xml)
            built.append((block, bid, x))
            x += 200

        for i in range(len(built) - 1):
            src_b, _, src_x = built[i]
            dst_b, _, dst_x = built[i + 1]
            cid = ids.next()
            conn_x = src_x + 30
            dx = dst_x - src_x - 30
            connectors += _connector(cid, i, pkg,
                                     src_b['name'], src_b['type'],
                                     dst_b['name'], dst_b['type'],
                                     conn_x, 80, dx)

    return embedded, connectors


class AnyLogicModelBuilder:
    """Builds AnyLogic .alp files matching AnyLogic 8.9.8 output format."""

    def build_model(self, definition: ModelDefinition) -> bytes:
        ids = _IDs()
        pkg = _java_pkg(definition.name)

        model_id   = ids.next()
        db_id      = ids.next()
        frame_id   = ids.next()
        main_id    = ids.next()
        main_gp    = ids.next()
        main_ds    = ids.next()
        scale_id   = ids.next()
        link_id    = ids.next()
        main_lvl   = ids.next()

        entity_gp_ids: Dict[str, int] = {}
        entity_classes_xml = ''
        for at in definition.agent_types:
            eid     = ids.next()
            gp_id   = ids.next()
            ent_ds  = ids.next()
            ent_sc  = ids.next()
            ent_lnk = ids.next()
            ent_lvl = ids.next()
            entity_gp_ids[at['name']] = gp_id
            entity_classes_xml += _active_object_class(
                eid, at['name'], gp_id, ent_ds, ent_sc, ent_lnk, ent_lvl,
                is_main=False, embedded='', connectors=''
            )

        embedded, connectors = _build_flow(
            definition.agent_types, pkg, ids, entity_gp_ids
        )

        plot_id     = ids.next()
        rec_id      = ids.next()
        chart_series = _collect_chart_series(definition.agent_types)
        datasets_xml = ''
        for i, s in enumerate(chart_series):
            ds_id_chart = ids.next()
            datasets_xml += _dataset_expression(i, s['title'], s['expression'], s['color'], ds_id_chart)
        time_plot_xml = _time_plot(plot_id, rec_id, datasets_xml) if chart_series else ''

        main_xml = _active_object_class(
            main_id, 'Main', main_gp, main_ds, scale_id, link_id, main_lvl,
            is_main=True, embedded=embedded, connectors=connectors,
            time_plot_xml=time_plot_xml
        )

        exp_id      = ids.next()
        run_id      = ids.next()
        stop_time   = int(definition.duration)

        converters_xml = '\n'.join(f'\t<Uuid>{u}</Uuid>' for u in _CONVERTER_UUIDS)

        xml = f"""\
<?xml version="1.0" encoding="UTF-8"?>
<!--
*************************************************
	         AnyLogic Project File
*************************************************
-->
<AnyLogicWorkspace WorkspaceVersion="1.9" AnyLogicVersion="8.9.8.202602271015" AlpVersion="8.9.7">
<Model>
	<Id>{model_id}</Id>
	<Name><![CDATA[{definition.name}]]></Name>
	<EngineVersion>6</EngineVersion>
	<JavaPackageName><![CDATA[{pkg}]]></JavaPackageName>
	<ModelTimeUnit><![CDATA[Minute]]></ModelTimeUnit>
	<Folders>
	</Folders>
	<ActiveObjectClasses>
		<!--   =========   Active Object Class   ========  -->
{main_xml}{entity_classes_xml}	</ActiveObjectClasses>
	<DifferentialEquationsMethod>EULER</DifferentialEquationsMethod>
	<MixedEquationsMethod>RK45_NEWTON</MixedEquationsMethod>
	<AlgebraicEquationsMethod>MODIFIED_NEWTON</AlgebraicEquationsMethod>
	<AbsoluteAccuracy>1.0E-5</AbsoluteAccuracy>
	<FixedTimeStep>0.001</FixedTimeStep>
	<RelativeAccuracy>1.0E-5</RelativeAccuracy>
	<TimeAccuracy>1.0E-5</TimeAccuracy>
	<InspectionWindowColorTheme>DEFAULT</InspectionWindowColorTheme>
	<Frame>
		<Id>{frame_id}</Id>
		<Width>1000</Width>
		<Height>600</Height>
	</Frame>
	<Database>
		<Id>{db_id}</Id>
		<Logging>false</Logging>
		<AutoExport>false</AutoExport>
		<ShutdownCompact>false</ShutdownCompact>
		<ImportSettings>
		</ImportSettings>
		<ExportSettings>
		</ExportSettings>
	</Database>

	<RunConfiguration ActiveObjectClassId="{main_id}">
		<Id>{run_id}</Id>
		<Name><![CDATA[RunConfiguration]]></Name>
		<MaximumMemory>512</MaximumMemory>
		<ModelTimeProperties>
			<StopOption><![CDATA[Stop at specified time]]></StopOption>
			<InitialDate><![CDATA[1779235200000]]></InitialDate>
			<InitialTime><![CDATA[0.0]]></InitialTime>
			<FinalDate><![CDATA[1781913600000]]></FinalDate>
			<FinalTime><![CDATA[{stop_time}.0]]></FinalTime>
		</ModelTimeProperties>
		<AnimationProperties>
			<StopNever>true</StopNever>
			<ExecutionMode>realTimeScaled</ExecutionMode>
			<RealTimeScale>1.0</RealTimeScale>
			<EnableZoomAndPanning>true</EnableZoomAndPanning>
			<EnableDeveloperPanel>false</EnableDeveloperPanel>
			<ShowDeveloperPanelOnStart>false</ShowDeveloperPanelOnStart>
		</AnimationProperties>
		<Inputs>
		</Inputs>
		<Outputs>
		</Outputs>
	</RunConfiguration>
	<Experiments>
		<!--   =========   Simulation Experiment   ========  -->
		<SimulationExperiment ActiveObjectClassId="{main_id}">
			<Id>{exp_id}</Id>
			<Name><![CDATA[Simulation]]></Name>
			<CommandLineArguments><![CDATA[]]></CommandLineArguments>
			<MaximumMemory>512</MaximumMemory>
			<RandomNumberGenerationType>fixedSeed</RandomNumberGenerationType>
			<CustomGeneratorCode>new Random()</CustomGeneratorCode>
			<SeedValue>1</SeedValue>
			<SelectionModeForSimultaneousEvents>LIFO</SelectionModeForSimultaneousEvents>
			<VmArgs><![CDATA[]]></VmArgs>
			<LoadRootFromSnapshot>false</LoadRootFromSnapshot>

			<Parameters>
			</Parameters>
			<PresentationProperties>
				<EnableZoomAndPanning>true</EnableZoomAndPanning>
				<ExecutionMode><![CDATA[realTimeScaled]]></ExecutionMode>
				<Title><![CDATA[{definition.name} : Simulation]]></Title>
				<EnableDeveloperPanel>true</EnableDeveloperPanel>
				<ShowDeveloperPanelOnStart>false</ShowDeveloperPanelOnStart>
				<RealTimeScale>1.0</RealTimeScale>
			</PresentationProperties>
			<ModelTimeProperties>
				<StopOption><![CDATA[Never]]></StopOption>
				<InitialDate><![CDATA[1779235200000]]></InitialDate>
				<InitialTime><![CDATA[0.0]]></InitialTime>
				<FinalDate><![CDATA[1781913600000]]></FinalDate>
				<FinalTime><![CDATA[{stop_time}.0]]></FinalTime>
			</ModelTimeProperties>
			<BypassInitialScreen>true</BypassInitialScreen>
		</SimulationExperiment>
	</Experiments>
    <RequiredLibraryReference>
		<LibraryName><![CDATA[com.anylogic.libraries.modules.markup_descriptors]]></LibraryName>
		<VersionMajor>1</VersionMajor>
		<VersionMinor>0</VersionMinor>
		<VersionBuild>0</VersionBuild>
    </RequiredLibraryReference>
    <RequiredLibraryReference>
		<LibraryName><![CDATA[com.anylogic.libraries.processmodeling]]></LibraryName>
		<VersionMajor>8</VersionMajor>
		<VersionMinor>0</VersionMinor>
		<VersionBuild>5</VersionBuild>
    </RequiredLibraryReference>
</Model>
<ConvertersApplied>
{converters_xml}
</ConvertersApplied>
</AnyLogicWorkspace>"""

        return xml.encode('utf-8')

    def build_from_template(self, template_name: str, params: Dict[str, Any]) -> bytes:
        templates = {
            'simple_queue': self._template_simple_queue,
            'factory':      self._template_factory,
            'warehouse':    self._template_warehouse,
            'hospital':     self._template_hospital,
        }
        fn = templates.get(template_name)
        if not fn:
            raise ValueError(f"Unknown template: {template_name}")
        return self.build_model(fn(params))

    def _template_simple_queue(self, params: Dict[str, Any]) -> ModelDefinition:
        # interarrivalTime is treated as RATE by AnyLogic → pass 1/mean
        # 1 server, mean service 3 min → ρ = (1/5) / (1/3) = 0.6
        return ModelDefinition(
            name=params.get('name', 'Simple_Queue'),
            description=params.get('description', 'Single server queue'),
            duration=params.get('duration', 480),
            agent_types=[{'name': 'Customer', 'blocks': [
                {'type': 'Source', 'name': 'source',
                 'params': {'interarrivalTime': params.get('arrival_rate', 'exponential(1.0/5.0)')}},
                {'type': 'Delay',  'name': 'service',
                 'params': {'capacity': str(params.get('num_servers', 1)),
                            'delayTime': params.get('service_time', 'triangular(2,3,4)')}},
                {'type': 'Sink',   'name': 'sink', 'params': {}},
            ]}]
        )

    def _template_factory(self, params: Dict[str, Any]) -> ModelDefinition:
        # interarrivalTime is treated as RATE → pass 1/mean
        # bottleneck machineA mean 8.33 min → ρ = (1/10) / (1/8.33) = 0.83
        return ModelDefinition(
            name=params.get('name', 'Factory'),
            description=params.get('description', 'Factory production line'),
            duration=params.get('duration', 480),
            agent_types=[{'name': 'Part', 'blocks': [
                {'type': 'Source', 'name': 'source',
                 'params': {'interarrivalTime': 'exponential(1.0/10.0)'}},
                {'type': 'Delay',  'name': 'machineA',
                 'params': {'capacity': '1', 'delayTime': 'triangular(5,8,12)'}},
                {'type': 'Delay',  'name': 'machineB',
                 'params': {'capacity': '1', 'delayTime': 'triangular(3,5,8)'}},
                {'type': 'Sink',   'name': 'sink', 'params': {}},
            ]}]
        )

    def _template_warehouse(self, params: Dict[str, Any]) -> ModelDefinition:
        # interarrivalTime is treated as RATE by AnyLogic → pass 1/mean
        # 3 docks, mean service 45 min → ρ = (1/20) / (3/45) = 0.75
        num_docks = params.get('num_docks', 3)
        return ModelDefinition(
            name=params.get('name', 'Warehouse'),
            description=params.get('description',
                                   f'Warehouse with {num_docks} loading docks'),
            duration=params.get('duration', 480),
            agent_types=[{'name': 'Truck', 'blocks': [
                {'type': 'Source', 'name': 'source',
                 'params': {'interarrivalTime': f'exponential(1.0/20.0)'}},
                {'type': 'Delay',  'name': 'service',
                 'params': {'capacity': str(num_docks),
                            'delayTime': 'triangular( 30, 45, 60 )'}},
                {'type': 'Sink',   'name': 'sink', 'params': {}},
            ]}]
        )

    def _template_hospital(self, params: Dict[str, Any]) -> ModelDefinition:
        # interarrivalTime is treated as RATE → pass 1/mean
        # bottleneck treatment: 3 servers mean 31.67 min → ρ = (1/12) / (3/31.67) = 0.88
        return ModelDefinition(
            name=params.get('name', 'Hospital_ER'),
            description=params.get('description', 'Hospital emergency room'),
            duration=params.get('duration', 480),
            agent_types=[{'name': 'Patient', 'blocks': [
                {'type': 'Source', 'name': 'source',
                 'params': {'interarrivalTime': 'exponential(1.0/12.0)'}},
                {'type': 'Delay',  'name': 'triage',
                 'params': {'capacity': '1', 'delayTime': 'triangular(5,8,12)'}},
                {'type': 'Delay',  'name': 'treatment',
                 'params': {'capacity': '3', 'delayTime': 'triangular(20,30,45)'}},
                {'type': 'Sink',   'name': 'sink', 'params': {}},
            ]}]
        )
