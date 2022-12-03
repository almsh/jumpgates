from utils.amount import get_bridgeable_amount
from utils.config import BRIDGE_DUST_CUTOFF_DECIMALS, BRIDGING_CAP
from utils.constants import one_quintillion
from utils.encode import get_address_encoder
import pytest


def test_bridge_polygon(
        jumpgate_polygon,
        ldo,
        ldo_holder,
        polygon_bridge,
        polygon_bridge_ldo_predicate
):
    ldo_predicate_address = polygon_bridge_ldo_predicate.address

    send_amount = 200 * 10**18
    # transfer tokens the jumpgate
    ldo.transfer(jumpgate_polygon.address, send_amount, {"from": ldo_holder})
    assert ldo.balanceOf(jumpgate_polygon.address) == send_amount

    bridge_balance_before = ldo.balanceOf(ldo_predicate_address)

    bridgeable_amount = get_bridgeable_amount(send_amount, ldo.decimals())
    # outstanding = bridge.outstandingBridged()

    # bridgeTokens
    tx = jumpgate_polygon.bridgeTokens()

    assert "Approval" in tx.events
    assert tx.events["Approval"]["_owner"] == jumpgate_polygon.address
    assert tx.events["Approval"]["_spender"] == ldo_predicate_address #
    assert tx.events["Approval"]["_amount"] == bridgeable_amount

    assert "Transfer" in tx.events
    assert tx.events["Transfer"]["_from"] == jumpgate_polygon.address
    assert tx.events["Transfer"]["_to"] == ldo_predicate_address
    assert tx.events["Transfer"]["_amount"] == bridgeable_amount

    assert ldo.balanceOf(jumpgate_polygon.address) == send_amount - bridgeable_amount
    assert (
        ldo.balanceOf(ldo_predicate_address) == bridge_balance_before + bridgeable_amount
    )

    assert "TokensBridged" in tx.events
    assert tx.events["TokensBridged"]["_token"] == ldo.address
    assert tx.events["TokensBridged"]["_bridge"] == polygon_bridge.address
    assert tx.events["TokensBridged"]["_recipient"] == jumpgate_polygon.recipient()
    assert tx.events["TokensBridged"]["_amount"] == bridgeable_amount
