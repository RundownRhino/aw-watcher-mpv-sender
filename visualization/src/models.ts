import { IEvent } from "aw-client";

export declare type CurplayingHeartbeatData = {
    filename: string,
    title: string
};

export interface CurplayingHeartbeat extends IEvent {
    data: CurplayingHeartbeatData
}