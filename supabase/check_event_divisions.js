import supabase from './supabase_client.js';

// Function to get all events with their competition info
async function getAllEvents() {
  try {
    const { data, error } = await supabase
      .from('event')
      .select(`
        id,
        year,
        start_date,
        end_date,
        competition!inner(id, name, name_key)
      `)
      .order('year', { ascending: false })
      .order('start_date', { ascending: true });
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching events:', error);
    throw error;
  }
}

// Function to get divisions for a specific event
async function getDivisionsForEvent(eventId) {
  try {
    const { data, error } = await supabase
      .from('division')
      .select(`
        id,
        category!inner(
          id,
          category_type!inner(name_key),
          category_weight!inner(name)
        )
      `)
      .eq('event_id', eventId);
    
    if (error) {
      throw error;
    }
    
    return data;
  } catch (error) {
    console.error(`Error fetching divisions for event ${eventId}:`, error);
    return [];
  }
}

// Function to format division info for display
function formatDivisionInfo(divisions) {
  if (!divisions || divisions.length === 0) {
    return '❌ NO DIVISIONS';
  }
  
  const divisionNames = divisions.map(div => {
    const typeKey = div.category?.category_type?.name_key || 'unknown';
    const weight = div.category?.category_weight?.name || 'unknown';
    return `${typeKey} ${weight}`;
  });
  
  return `✅ ${divisions.length} divisions: ${divisionNames.join(', ')}`;
}

export async function checkEventDivisions() {
  try {
    console.log('Checking events for division entries...\n');
    
    // Get all events
    const events = await getAllEvents();
    console.log(`Found ${events.length} total events\n`);
    
    let eventsWithDivisions = 0;
    let eventsWithoutDivisions = 0;
    let totalDivisions = 0;
    
    // Check each event
    for (let i = 0; i < events.length; i++) {
      const event = events[i];
      const divisions = await getDivisionsForEvent(event.id);
      
      const hasDivisions = divisions.length > 0;
      if (hasDivisions) {
        eventsWithDivisions++;
        totalDivisions += divisions.length;
      } else {
        eventsWithoutDivisions++;
      }
      
      // Format event info
      const eventDate = event.start_date ? 
        (event.end_date && event.start_date !== event.end_date ? 
          `${event.start_date} to ${event.end_date}` : 
          event.start_date) : 
        'No date';
      
      const eventInfo = `${event.competition.name} (${event.competition.name_key}) - ${eventDate}`;
      const divisionInfo = formatDivisionInfo(divisions);
      
      console.log(`${i + 1}. ${eventInfo}`);
      console.log(`   ${divisionInfo}\n`);
      
      // Add a small delay to avoid overwhelming the database
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    // Summary
    console.log('='.repeat(60));
    console.log('SUMMARY:');
    console.log(`Total events: ${events.length}`);
    console.log(`Events with divisions: ${eventsWithDivisions}`);
    console.log(`Events without divisions: ${eventsWithoutDivisions}`);
    console.log(`Total divisions created: ${totalDivisions}`);
    console.log(`Average divisions per event: ${eventsWithDivisions > 0 ? (totalDivisions / eventsWithDivisions).toFixed(1) : 0}`);
    
    if (eventsWithoutDivisions > 0) {
      console.log(`\n⚠️  ${eventsWithoutDivisions} events are missing divisions!`);
    } else {
      console.log(`\n✅ All events have divisions!`);
    }
    
    return {
      totalEvents: events.length,
      eventsWithDivisions,
      eventsWithoutDivisions,
      totalDivisions
    };
    
  } catch (error) {
    console.error('Error in checkEventDivisions:', error);
    throw error;
  }
}

// Function to check only 2025 events
export async function check2025EventDivisions() {
  try {
    console.log('Checking 2025 events for division entries...\n');
    
    // Get only 2025 events
    const { data: events, error } = await supabase
      .from('event')
      .select(`
        id,
        year,
        start_date,
        end_date,
        competition!inner(id, name, name_key)
      `)
      .eq('year', 2025)
      .order('start_date', { ascending: true });
    
    if (error) {
      throw error;
    }
    
    console.log(`Found ${events.length} events in 2025\n`);
    
    let eventsWithDivisions = 0;
    let eventsWithoutDivisions = 0;
    let totalDivisions = 0;
    
    // Check each event
    for (let i = 0; i < events.length; i++) {
      const event = events[i];
      const divisions = await getDivisionsForEvent(event.id);
      
      const hasDivisions = divisions.length > 0;
      if (hasDivisions) {
        eventsWithDivisions++;
        totalDivisions += divisions.length;
      } else {
        eventsWithoutDivisions++;
      }
      
      // Format event info
      const eventDate = event.start_date ? 
        (event.end_date && event.start_date !== event.end_date ? 
          `${event.start_date} to ${event.end_date}` : 
          event.start_date) : 
        'No date';
      
      const eventInfo = `${event.competition.name} (${event.competition.name_key}) - ${eventDate}`;
      const divisionInfo = formatDivisionInfo(divisions);
      
      console.log(`${i + 1}. ${eventInfo}`);
      console.log(`   ${divisionInfo}\n`);
      
      // Add a small delay to avoid overwhelming the database
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    // Summary
    console.log('='.repeat(60));
    console.log('2025 EVENTS SUMMARY:');
    console.log(`Total 2025 events: ${events.length}`);
    console.log(`Events with divisions: ${eventsWithDivisions}`);
    console.log(`Events without divisions: ${eventsWithoutDivisions}`);
    console.log(`Total divisions created: ${totalDivisions}`);
    console.log(`Average divisions per event: ${eventsWithDivisions > 0 ? (totalDivisions / eventsWithDivisions).toFixed(1) : 0}`);
    
    if (eventsWithoutDivisions > 0) {
      console.log(`\n⚠️  ${eventsWithoutDivisions} 2025 events are missing divisions!`);
    } else {
      console.log(`\n✅ All 2025 events have divisions!`);
    }
    
    return {
      totalEvents: events.length,
      eventsWithDivisions,
      eventsWithoutDivisions,
      totalDivisions
    };
    
  } catch (error) {
    console.error('Error in check2025EventDivisions:', error);
    throw error;
  }
}

// Example usage
if (import.meta.main) {
  const args = Deno.args;
  const mode = args[0] || '2025'; // 'all' or '2025'
  
  if (mode === 'all') {
    checkEventDivisions()
      .then(() => console.log('Event divisions check completed successfully'))
      .catch(error => console.error('Event divisions check failed:', error));
  } else {
    check2025EventDivisions()
      .then(() => console.log('2025 event divisions check completed successfully'))
      .catch(error => console.error('2025 event divisions check failed:', error));
  }
} 