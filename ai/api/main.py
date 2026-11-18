"""FastAPI on port 8000. Omar owns the process. Ola owns search, vocabulary, and labels."""

from fastapi import FastAPI

app = FastAPI(title="SHAWAF inference")

# Phase 1 routes, all under /internal/v1. Add the handler on the owning ticket.
# POST /processing-jobs                         Omar, SCRUM-134
# POST /search                                  Ola, SCRUM-139
# GET  /vocabulary                              Ola, SCRUM-131
# GET  /live-events/labels                      Ola, SCRUM-131
# POST /clip-jobs                               Omar, SCRUM-136
# PUT  /live-streams/{cameraId}                 Omar, SCRUM-130
# DELETE /live-streams/{cameraId}               Omar, SCRUM-130
# GET  /live-streams                            Omar, SCRUM-130
# GET  /health/ready                            Omar, SCRUM-130
# GET  /processing-jobs/{jobId}                 Phase 2, SCRUM-128
# GET  /clip-jobs/{clipJobId}                   Phase 2, SCRUM-142
