// Basic event types
export interface SlackEventBase {
    type: string;
    user: string;
    text: string;
    ts: string;
    channel: string;
    event_ts: string;
}

// App mention event
export interface AppMentionEvent extends SlackEventBase {
    type: 'app_mention';
}

// Event wrapper for all event types
export interface SlackEventWrapper<T = AppMentionEvent> {
    token: string;
    team_id: string;
    api_app_id: string;
    event: T;
    type: 'event_callback';
    event_id: string;
    event_time: number;
    authed_users: string[];
}

// Challenge request for URL verification
export interface SlackUrlVerificationRequest {
    token: string;
    challenge: string;
    type: 'url_verification';
}

// Union type for all possible Slack request types
export type SlackRequestPayload = SlackEventWrapper | SlackUrlVerificationRequest;

// Type guard to check if the request is a URL verification request
export function isUrlVerificationRequest(payload: SlackRequestPayload): payload is SlackUrlVerificationRequest {
    return payload.type === 'url_verification';
}

// Type guard to check if the request is an event wrapper
export function isEventWrapper(payload: SlackRequestPayload): payload is SlackEventWrapper {
    return payload.type === 'event_callback';
}

// Type guard to check if an event is an app mention
export function isAppMentionEvent(event: SlackEventBase): event is AppMentionEvent {
    return event.type === 'app_mention';
} 