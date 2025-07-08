/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";

export class VaultTokenWidget extends Component {
    setup() {
        // Inicializa el estado con el valor actual del token.
        this.state = useState({
            token: this.props.record.data.token || ""
        });
    }

    // onWillUpdate es un método del ciclo de vida del componente.
    onWillUpdate(nextProps) {
        const newToken = nextProps.record.data.token || "";
        if (this.state.token !== newToken) {
            this.state.token = newToken;
        }
    }
}

VaultTokenWidget.template = "rainbow.VaultTokenWidget";
VaultTokenWidget.supportedTypes = ["char"];

export const vaultTokenWidget = {
    component: VaultTokenWidget,
};

registry.category("fields").add("vault_token_widget", vaultTokenWidget);