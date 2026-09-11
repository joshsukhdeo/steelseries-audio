import sys
import importlib.util
import importlib.machinery
from unittest.mock import patch

loader = importlib.machinery.SourceFileLoader("steelseries", "/home/tay/projects/steelseries-audio/steelseries-audio")
spec = importlib.util.spec_from_loader("steelseries", loader)
ss = importlib.util.module_from_spec(spec)
loader.exec_module(ss)

def test_get_sinks():
    mock_nodes = [
        {"type": "PipeWire:Interface:Node", "info": {"id": 1, "props": {"node.name": "bluez_output.mac1", "node.description": "Arena 7"}}},
        {"type": "PipeWire:Interface:Node", "info": {"id": 2, "props": {"node.name": "bluez_output.mac2", "node.description": "Sony XM4"}}},
        {"type": "PipeWire:Interface:Node", "info": {"id": 3, "props": {"node.name": "steelseries_arena7_dsp", "node.description": "DSP"}}},
    ]
    
    with patch.object(ss, "get_pw_nodes", return_value=mock_nodes):
        # Should return a list of matching physical sinks and the DSP info
        phys_sinks, dsp_id, dsp_name = ss.get_sinks(target_names=["Sony XM4"])
        assert len(phys_sinks) == 1
        assert phys_sinks[0]["id"] == 2
        assert phys_sinks[0]["name"] == "bluez_output.mac2"
        assert phys_sinks[0]["type"] == "Bluetooth"

def test_generate_wp_conf():
    conf = ss.generate_wp_conf(["Sony XM4"])
    assert "Sony XM4" in conf
    assert "Arena 7" not in conf

def test_generate_dsp_conf():
    conf = ss.generate_dsp_conf("audiophile", target_node="bluez_output.mac2")
    assert "target.object" in conf and "bluez_output.mac2" in conf

if __name__ == "__main__":
    test_get_sinks()
    test_generate_wp_conf()
    test_generate_dsp_conf()
    print("Tests passed.")
