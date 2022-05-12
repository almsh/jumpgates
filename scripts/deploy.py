from brownie import network, accounts, Jumpgate
import json
from utils.env import get_env

import utils.log as log
from utils.config import (
    SOLANA_WORMHOLE_CHAIN_ID,
    TERRA_WORMHOLE_CHAIN_ID,
)
from utils.encode import get_address_encoder


# environment
WEB3_INFURA_PROJECT_ID = get_env("WEB3_INFURA_PROJECT_ID")
ETHERSCAN_TOKEN = get_env("ETHERSCAN_TOKEN")

# deploy parameters
DEPLOYER = get_env("DEPLOYER")
NETWORK = get_env("NETWORK")
TOKEN = get_env("TOKEN")
BRIDGE = get_env("BRIDGE")
RECIPIENT_CHAIN = int(get_env("RECIPIENT_CHAIN"))
RECIPIENT = get_env("RECIPIENT")
ARBITER_FEE = get_env("ARBITER_FEE") or 0

SUPPORTED_CHAINS = [TERRA_WORMHOLE_CHAIN_ID, SOLANA_WORMHOLE_CHAIN_ID]


def main():
    log.info("Checking environment variables...")

    if not WEB3_INFURA_PROJECT_ID:
        log.error("`WEB3_INFURA_PROJECT_ID` not found!")
        return

    if not ETHERSCAN_TOKEN:
        log.error("`ETHERSCAN_TOKEN` not found!")
        return

    log.okay("Environment variables are present!")

    log.info("Checking deploy parameters...")

    if not NETWORK:
        log.error("`NETWORK` not found!")
        return

    if network.show_active() != NETWORK:
        log.error(f"Wrong network! Expected `{NETWORK}` but got", network.show_active())
        return

    if not DEPLOYER:
        log.error("`DEPLOYER` not found!")
        return

    try:
        deployer = accounts.load(DEPLOYER)
    except FileNotFoundError:
        log.error(f"Local account with id `{DEPLOYER}` not found!")
        return

    if not TOKEN:
        log.error("`TOKEN` not found!")
        return

    if not BRIDGE:
        log.error("`BRIDGE` not found!")
        return

    if not RECIPIENT_CHAIN:
        log.error("`RECIPIENT_CHAIN` not found!")
        return

    if RECIPIENT_CHAIN not in SUPPORTED_CHAINS:
        log.error("`RECIPIENT_CHAIN` not supported!")
        return

    if not RECIPIENT:
        log.error("`RECIPIENT` not found!")
        return

    log.okay("Deploy parameters are present!")

    log.info("NETWORK", NETWORK)
    log.info("DEPLOYER", deployer.address)
    log.info("TOKEN", TOKEN)
    log.info("BRIDGE", BRIDGE)
    log.info("RECIPIENT_CHAIN", RECIPIENT_CHAIN)
    log.info("RECIPIENT", RECIPIENT)
    log.info("ARBITER_FEE", ARBITER_FEE)

    proceed = log.prompt_yes_no("Proceed?")

    if not proceed:
        log.error("Script stopped!")
        return

    log.okay("Proceeding...")

    log.info(f"Deploying Jumpgate...")

    encode_address = get_address_encoder(RECIPIENT_CHAIN)

    token = TOKEN
    bridge = BRIDGE
    recipientChain = RECIPIENT_CHAIN
    recipient = encode_address(RECIPIENT)
    arbiterFee = ARBITER_FEE

    jumpgate = Jumpgate.deploy(
        deployer.address,
        token,
        bridge,
        recipientChain,
        recipient,
        arbiterFee,
        {"from": deployer},
        publish_source=bool(ETHERSCAN_TOKEN),
    )

    log.okay("Jumpgate deployed successfully!")

    deployed_filename = f"./deployed/{network.show_active()}-{RECIPIENT}.json"
    with open(deployed_filename, "w") as outfile:
        json.dump(
            {
                "jumpgate": jumpgate.address,
                "token": token,
                "bridge": bridge,
                "recipientChain": recipientChain,
                "recipient": RECIPIENT,
                "arbiterFee": arbiterFee,
            },
            outfile,
        )

    log.okay("Deploy data dumped to", deployed_filename)
