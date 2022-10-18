import { OnInit, ChangeDetectorRef } from "@angular/core";
import { Service } from '@wiz/libs/season/service';

export class Component implements OnInit {

    public releases: any = [];

    constructor(
        public service: Service,
        public ref: ChangeDetectorRef
    ) { }

    public async ngOnInit() {
        await this.service.init();
        await this.service.auth.allow('admin', '/');

        this.releases.push({
            name: "v2022.10.18.1547",
            log: [
                "[workflow] full change ui / ux",
                "[workflow] angular.js to angular upgrade",
                "[core] apply WIZ 2.0"
            ]
        });

        this.releases.push({
            name: "v2022.08.25.2154",
            log: [
                "[workflow] kernelspec error fixed in package install"
            ]
        });

        this.releases.push({
            name: "v2022.08.23.2317",
            log: [
                "[workflow] timer bug fixed (display by each workflow)"
            ]
        });

        this.releases.push({
            name: "v2022.08.23.2129",
            log: [
                "[workflow] fold codeflow when block > 5",
                "[workflow] app title editable",
                "[workflow] input/output sortable bug fixed"
            ]
        });

        this.releases.push({
            name: "v2022.08.23.2109",
            log: [
                "[workflow] customizable codeflow title",
                "[workflow] drag & drop sorting in codeflow",
                "[workflow] mobile optimized",
                "[workflow] enhanced flow status update",
                "[workflow] auto select kernel when single kernel"
            ]
        });

        this.releases.push({
            name: "v2022.08.23.1933",
            log: [
                "[workflow] add textarea option at flow input"
            ]
        });

        this.releases.push({
            name: "v2022.08.23.1808",
            log: [
                "[workflow] input/output validate bug fixed",
                "[workflow] app asc sorted by title",
                "[workflow] flow status trigger (for fix error)",
                "[workflow] support UI Mode on mobile"
            ]
        });

        this.releases.push({
            name: "v2022.08.23.1536",
            log: [
                "[admin] Releases Info",
                "[admin] UI / Core version update on web setting"
            ]
        });

        await this.service.render();
    }
}