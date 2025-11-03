import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Users, UserPlus, Mail, Shield, Trash2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '../components/ui/table';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { apiCall } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

export default function TeamSettings() {
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  const [workspace, setWorkspace] = useState(null);
  const [members, setMembers] = useState([]);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('member');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTeam();
  }, []);

  const loadTeam = async () => {
    try {
      const response = await apiCall('/api/team/workspace');
      const data = await response.json();
      setWorkspace(data.workspace);
      setMembers(data.members || []);
      setLoading(false);
    } catch (error) {
      setLoading(false);
    }
  };

  const sendInvite = async () => {
    if (!inviteEmail) {
      toast.error('Please enter an email address');
      return;
    }

    try {
      await apiCall('/api/team/invite', {
        method: 'POST',
        body: JSON.stringify({ email: inviteEmail, role: inviteRole })
      });
      toast.success('Invitation sent!');
      setInviteEmail('');
      loadTeam();
    } catch (error) {
      toast.error('Failed to send invitation');
    }
  };

  const removeMember = async (memberId) => {
    try {
      await apiCall(`/api/team/members/${memberId}`, { method: 'DELETE' });
      toast.success('Member removed');
      loadTeam();
    } catch (error) {
      toast.error('Failed to remove member');
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/')}>
              <Sparkles className="h-6 w-6 text-primary" />
              <span className="font-heading text-xl font-bold">GR8 AI Automation</span>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="ghost" onClick={() => navigate('/dashboard')}>Dashboard</Button>
              <Button variant="ghost" onClick={logout}>Logout</Button>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="font-heading text-3xl font-bold">Team & Workspace</h1>
          <p className="text-muted-foreground mt-1">Manage team members and collaboration</p>
        </div>

        {/* Workspace Info */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Workspace Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Workspace Name:</span>
                <span className="font-semibold">{workspace?.name || user?.name + "'s Workspace"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Plan:</span>
                <Badge>{user?.plan?.toUpperCase()}</Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Team Members:</span>
                <span className="font-semibold">{members.length + 1}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Invite Member */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <UserPlus className="h-5 w-5" />
              Invite Team Member
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <div className="flex-1">
                <Label>Email Address</Label>
                <Input
                  type="email"
                  placeholder="teammate@company.com"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                />
              </div>
              <div className="w-40">
                <Label>Role</Label>
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value)}
                  className="w-full px-3 py-2 border border-border rounded-md bg-background"
                >
                  <option value="member">Member</option>
                  <option value="admin">Admin</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>
              <div className="flex items-end">
                <Button onClick={sendInvite}>
                  <Mail className="h-4 w-4 mr-2" />
                  Send Invite
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Team Members */}
        <Card>
          <CardHeader>
            <CardTitle>Team Members</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {/* Owner */}
                <TableRow>
                  <TableCell className="font-medium">{user?.name} (You)</TableCell>
                  <TableCell>{user?.email}</TableCell>
                  <TableCell><Badge variant="destructive">Owner</Badge></TableCell>
                  <TableCell><Badge variant="default">Active</Badge></TableCell>
                  <TableCell className="text-right">-</TableCell>
                </TableRow>
                {/* Team members */}
                {members.map(member => (
                  <TableRow key={member._id}>
                    <TableCell>{member.name}</TableCell>
                    <TableCell>{member.email}</TableCell>
                    <TableCell><Badge className="capitalize">{member.role}</Badge></TableCell>
                    <TableCell>
                      <Badge variant={member.status === 'active' ? 'default' : 'secondary'}>
                        {member.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => removeMember(member._id)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            {members.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                No team members yet. Invite someone to collaborate!
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
