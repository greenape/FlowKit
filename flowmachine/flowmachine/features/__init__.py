# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Features (i.e. co-variates, indicators, metrics) are 
used as measurements of a phenomenon of interest.
This section of `flowmachine` contains code that calculates
a series of features.

"""
from .location import *
from .network import *
from .subscriber import *

from .raster import *
from .spatial import *

from .utilities import *

loc = ["TotalLocationEvents", "Flows", "UniqueSubscriberCounts", "LocationIntroversion"]
nw = ["TotalNetworkObjects", "AggregateNetworkObjects"]
subs = [
    "RadiusOfGyration",
    "NocturnalEvents",
    "TotalSubscriberEvents",
    "FirstLocation",
    "CallDays",
    "ModalLocation",
    "daily_location",
    "DayTrajectories",
    "LocationVisits",
    "NewSubscribers",
    "subscriber_location_cluster",
    "HartiganCluster",
    "UniqueLocationCounts",
    "SubscriberDegree",
    "TotalActivePeriodsSubscriber",
    "ContactBalance",
    "EventScore",
    "LabelEventScore",
    "SubscriberTACs",
    "SubscriberTAC",
    "SubscriberHandsets",
    "SubscriberHandset",
    "SubscriberPhoneType",
    "ParetoInteractions",
    "SubscriberCallDurations",
    "PairedSubscriberCallDurations",
    "PerLocationSubscriberCallDurations",
    "PairedPerLocationSubscriberCallDurations",
    "MostFrequentLocation",
    "LastLocation",
    "PeriodicEntropy",
    "LocationEntropy",
    "ContactEntropy",
    "EventCount",
    "MeaningfulLocations",
    "MeaningfulLocationsAggregate",
    "MeaningfulLocationsOD",
    "ProportionEventType",
    "PeriodicEntropy",
    "LocationEntropy",
    "ContactEntropy",
    "DistanceCounterparts",
    "MDSVolume",
    "ContactReciprocal",
    "ProportionContactReciprocal",
    "ProportionEventReciprocal",
]

rast = ["RasterStatistics"]
spat = [
    "LocationArea",
    "LocationCluster",
    "DistanceMatrix",
    "VersionedInfrastructure",
    "Grid",
    "CellToAdmin",
    "CellToPolygon",
    "CellToGrid",
    "Circle",
    "CircleGeometries",
]

ut = [
    "GroupValues",
    "feature_collection",
    "subscriber_locations",
    "EventTableSubset",
    "UniqueSubscribers",
    "EventsTablesUnion",
    "EventTableSubset",
]

sub_modules = ["location", "subscriber", "network", "utilities", "raster", "spatial"]

__all__ = loc + nw + subs + rast + ut + spat + sub_modules
